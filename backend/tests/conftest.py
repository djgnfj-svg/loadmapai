"""Pytest configuration and fixtures."""

import os
import pytest
from typing import Generator, Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Set test environment before importing app
os.environ["TESTING"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars-minimum-required"
os.environ["ANTHROPIC_API_KEY"] = "test-api-key"

from app.main import app
from app.db import Base, get_db, engine as app_engine
from app.models.user import User, AuthProvider
from app.core.security import get_password_hash, create_access_token

# Use the actual database engine (PostgreSQL) for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=app_engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    # Create tables
    Base.metadata.create_all(bind=app_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up test data by truncating tables
        with app_engine.connect() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
            conn.commit()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a verified test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=True,  # 이메일 인증 완료된 사용자
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def unverified_user(db: Session) -> User:
    """Create an unverified test user."""
    user = User(
        email="unverified@example.com",
        name="Unverified User",
        hashed_password=get_password_hash("testpassword123"),
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=False,  # 이메일 미인증 사용자
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """Create a JWT token for test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def authorized_client(client: TestClient, test_user_token: str) -> TestClient:
    """Create an authorized test client."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client


@pytest.fixture
def mock_anthropic() -> Generator[MagicMock, None, None]:
    """Mock Anthropic API calls."""
    with patch("langchain_anthropic.ChatAnthropic") as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Mocked AI response")
        mock.return_value = mock_instance
        yield mock
