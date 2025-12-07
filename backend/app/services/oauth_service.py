"""Google OAuth service for authentication."""
import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, AuthProvider
from app.core.security import create_access_token, create_refresh_token


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleOAuthService:
    """Service for Google OAuth authentication."""

    def __init__(self, db: Session):
        self.db = db

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        if state:
            params["state"] = state

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GOOGLE_AUTH_URL}?{query}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange authorization code for access tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        """Get user info from Google using access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    def get_or_create_user(self, google_user: dict) -> User:
        """Get existing user or create new one from Google user info."""
        email = google_user.get("email")
        if not email:
            raise ValueError("Email not provided by Google")

        # Check if user exists
        user = self.db.query(User).filter(User.email == email).first()

        if user:
            # Update user info if needed
            if user.auth_provider == AuthProvider.EMAIL:
                # User registered with email, link Google account
                user.auth_provider = AuthProvider.GOOGLE
            if not user.avatar_url and google_user.get("picture"):
                user.avatar_url = google_user.get("picture")
            if not user.name and google_user.get("name"):
                user.name = google_user.get("name")
            self.db.commit()
            self.db.refresh(user)
            return user

        # Create new user
        user = User(
            email=email,
            name=google_user.get("name", email.split("@")[0]),
            avatar_url=google_user.get("picture"),
            auth_provider=AuthProvider.GOOGLE,
            is_active=True,
            is_verified=True,  # Google accounts are pre-verified
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user."""
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
