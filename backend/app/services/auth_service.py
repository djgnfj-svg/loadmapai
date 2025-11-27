from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID

from app.models.user import User, AuthProvider
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=get_password_hash(user_data.password),
            auth_provider=AuthProvider.EMAIL,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_oauth_user(
        self,
        email: str,
        name: str,
        provider: AuthProvider,
        provider_id: str,
        avatar_url: Optional[str] = None,
    ) -> User:
        # Check if user already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            # Update provider info if user exists
            existing_user.auth_provider = provider
            existing_user.provider_id = provider_id
            if avatar_url:
                existing_user.avatar_url = avatar_url
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user

        # Create new OAuth user
        user = User(
            email=email,
            name=name,
            auth_provider=provider,
            provider_id=provider_id,
            avatar_url=avatar_url,
            is_verified=True,  # OAuth users are verified
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
