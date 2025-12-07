"""OAuth authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.config import settings
from app.services.oauth_service import GoogleOAuthService
from app.schemas.auth import AuthResponse


router = APIRouter()


class OAuthUrlResponse(BaseModel):
    """OAuth authorization URL response."""
    url: str


@router.get("/google/url", response_model=OAuthUrlResponse)
async def get_google_auth_url(
    state: str = Query(None, description="Optional state parameter for CSRF protection"),
    db: Session = Depends(get_db),
):
    """Get Google OAuth authorization URL.

    프론트엔드에서 이 URL로 사용자를 리다이렉트하면 Google 로그인 페이지가 표시됩니다.
    """
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    service = GoogleOAuthService(db)
    url = service.get_authorization_url(state=state)
    return OAuthUrlResponse(url=url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(None, description="State parameter for CSRF protection"),
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback.

    Google에서 리다이렉트된 후 호출됩니다.
    인증 코드를 토큰으로 교환하고 사용자를 생성/조회합니다.
    프론트엔드로 토큰과 함께 리다이렉트합니다.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    service = GoogleOAuthService(db)

    try:
        # Exchange code for tokens
        tokens = await service.exchange_code_for_tokens(code)
        google_access_token = tokens.get("access_token")

        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google",
            )

        # Get user info from Google
        google_user = await service.get_user_info(google_access_token)

        # Get or create user
        user = service.get_or_create_user(google_user)

        # Create our tokens
        app_tokens = service.create_tokens(user)

        # Redirect to frontend with tokens
        frontend_callback_url = (
            f"{settings.frontend_url}/oauth/callback"
            f"?access_token={app_tokens['access_token']}"
            f"&refresh_token={app_tokens['refresh_token']}"
        )
        if state:
            frontend_callback_url += f"&state={state}"

        return RedirectResponse(url=frontend_callback_url)

    except HTTPException:
        raise
    except Exception as e:
        # Redirect to frontend with error
        error_url = f"{settings.frontend_url}/oauth/callback?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/google/token", response_model=AuthResponse)
async def google_token_login(
    code: str = Query(..., description="Authorization code from Google"),
    db: Session = Depends(get_db),
):
    """Exchange Google auth code for app tokens (API-only flow).

    모바일 앱이나 SPA에서 직접 토큰을 받고 싶을 때 사용합니다.
    리다이렉트 대신 JSON 응답을 반환합니다.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    service = GoogleOAuthService(db)

    try:
        # Exchange code for tokens
        tokens = await service.exchange_code_for_tokens(code)
        google_access_token = tokens.get("access_token")

        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google",
            )

        # Get user info from Google
        google_user = await service.get_user_info(google_access_token)

        # Get or create user
        user = service.get_or_create_user(google_user)

        # Create our tokens
        app_tokens = service.create_tokens(user)

        return AuthResponse(
            user=user,
            access_token=app_tokens["access_token"],
            refresh_token=app_tokens["refresh_token"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}",
        )
