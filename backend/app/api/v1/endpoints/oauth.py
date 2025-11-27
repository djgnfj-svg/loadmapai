from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
import httpx

from app.db import get_db
from app.config import settings
from app.models.user import AuthProvider
from app.core.oauth import oauth
from app.core.security import create_access_token, create_refresh_token
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/google")
async def google_login(request: Request):
    """Redirect to Google OAuth login."""
    redirect_uri = f"{settings.backend_url}/api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )

        # Create or update user
        auth_service = AuthService(db)
        user = auth_service.create_oauth_user(
            email=user_info['email'],
            name=user_info.get('name', user_info['email'].split('@')[0]),
            provider=AuthProvider.GOOGLE,
            provider_id=user_info['sub'],
            avatar_url=user_info.get('picture'),
        )

        # Create tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        # Redirect to frontend with tokens
        redirect_url = (
            f"{settings.frontend_url}/auth/callback"
            f"?access_token={access_token}"
            f"&refresh_token={refresh_token}"
        )
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # Redirect to frontend with error
        redirect_url = f"{settings.frontend_url}/login?error=oauth_failed"
        return RedirectResponse(url=redirect_url)


@router.get("/github")
async def github_login(request: Request):
    """Redirect to GitHub OAuth login."""
    redirect_uri = f"{settings.backend_url}/api/v1/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle GitHub OAuth callback."""
    try:
        token = await oauth.github.authorize_access_token(request)

        # Get user info from GitHub
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f"Bearer {token['access_token']}"},
            )
            user_data = resp.json()

            # Get email (may need separate call if email is private)
            email = user_data.get('email')
            if not email:
                email_resp = await client.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f"Bearer {token['access_token']}"},
                )
                emails = email_resp.json()
                # Get primary email
                for e in emails:
                    if e.get('primary'):
                        email = e['email']
                        break
                if not email and emails:
                    email = emails[0]['email']

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get email from GitHub",
            )

        # Create or update user
        auth_service = AuthService(db)
        user = auth_service.create_oauth_user(
            email=email,
            name=user_data.get('name') or user_data.get('login', email.split('@')[0]),
            provider=AuthProvider.GITHUB,
            provider_id=str(user_data['id']),
            avatar_url=user_data.get('avatar_url'),
        )

        # Create tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        # Redirect to frontend with tokens
        redirect_url = (
            f"{settings.frontend_url}/auth/callback"
            f"?access_token={access_token}"
            f"&refresh_token={refresh_token}"
        )
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # Redirect to frontend with error
        redirect_url = f"{settings.frontend_url}/login?error=oauth_failed"
        return RedirectResponse(url=redirect_url)
