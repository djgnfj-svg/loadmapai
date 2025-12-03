"""Tests for authentication API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.verification_service import VerificationService


class TestRegister:
    """Test user registration."""

    def test_register_success(self, client: TestClient):
        """Test successful user registration - sends verification email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        # 이제 토큰 대신 메시지와 이메일을 반환
        assert "message" in data
        assert "email" in data
        assert data["email"] == "newuser@example.com"
        # 토큰은 반환되지 않음 (이메일 인증 후에만 로그인 가능)
        assert "access_token" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "name": "Another User",
                "password": "password123",
            },
        )
        assert response.status_code == 400

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "name": "Test User",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test registration with short password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "short",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Test user login."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login with verified user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data

    def test_login_unverified_user(self, client: TestClient, unverified_user: User):
        """Test login fails for unverified user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": unverified_user.email,
                "password": "testpassword123",
            },
        )
        assert response.status_code == 403
        data = response.json()
        # 표준 에러 응답 또는 기본 HTTPException 응답 처리
        error_message = data.get("detail") or data.get("error", {}).get("message", "")
        assert "not verified" in error_message

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401


class TestMe:
    """Test get current user endpoint."""

    def test_me_authorized(self, authorized_client: TestClient, test_user: User):
        """Test getting current user info when authorized."""
        response = authorized_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    def test_me_unauthorized(self, client: TestClient):
        """Test getting current user info without authorization."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]

    def test_me_invalid_token(self, client: TestClient):
        """Test with invalid token."""
        client.headers["Authorization"] = "Bearer invalid-token"
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestEmailVerification:
    """Test email verification endpoints."""

    def test_verify_email_success(self, client: TestClient, db: Session, unverified_user: User):
        """Test successful email verification."""
        # 인증 토큰 생성
        verification_service = VerificationService(db)
        token = verification_service.create_verification_token(unverified_user)

        # 이메일 인증
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token.token},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 사용자 인증 상태 확인
        db.refresh(unverified_user)
        assert unverified_user.is_verified is True

    def test_verify_email_invalid_token(self, client: TestClient):
        """Test verification with invalid token."""
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": "invalid-token"},
        )
        assert response.status_code == 400

    def test_verify_email_expired_token(self, client: TestClient, db: Session, unverified_user: User):
        """Test verification with expired token."""
        from datetime import datetime, timedelta, timezone

        verification_service = VerificationService(db)
        token = verification_service.create_verification_token(unverified_user)

        # 토큰 만료 처리
        token.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()

        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token.token},
        )
        assert response.status_code == 400
        data = response.json()
        error_message = data.get("detail") or data.get("error", {}).get("message", "")
        assert "만료" in error_message

    def test_verify_email_already_used_token(self, client: TestClient, db: Session, unverified_user: User):
        """Test verification with already used token."""
        verification_service = VerificationService(db)
        token = verification_service.create_verification_token(unverified_user)

        # 첫 번째 인증 (성공)
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token.token},
        )
        assert response.status_code == 200

        # 두 번째 인증 (실패 - 이미 사용된 토큰)
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token.token},
        )
        assert response.status_code == 400

    def test_resend_verification_email(self, client: TestClient, unverified_user: User):
        """Test resending verification email."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            json={"email": unverified_user.email},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_resend_verification_already_verified(self, client: TestClient, test_user: User):
        """Test resending verification email for already verified user."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            json={"email": test_user.email},
        )
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert "이미 인증" in response.json()["message"]

    def test_resend_verification_nonexistent_email(self, client: TestClient):
        """Test resending verification email for non-existent user."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            json={"email": "nonexistent@example.com"},
        )
        # 보안상 성공 응답 반환
        assert response.status_code == 200
        assert response.json()["success"] is True
