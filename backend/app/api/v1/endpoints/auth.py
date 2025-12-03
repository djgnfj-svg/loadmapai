from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from uuid import UUID

from app.db import get_db
from app.config import settings
from app.models.user import User
from app.schemas import (
    UserCreate, UserLogin, UserUpdate, AuthResponse, UserResponse,
    RefreshTokenRequest, Token, TokenPayload,
    RegisterResponse, EmailVerificationRequest, EmailVerificationResponse,
    ResendVerificationRequest, ResendVerificationResponse,
)
from app.services.auth_service import AuthService
from app.services.verification_service import VerificationService
from app.core.security import create_access_token, create_refresh_token
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user with email and password.

    회원가입 후 인증 이메일이 발송됩니다.
    이메일 인증 완료 전까지 로그인이 불가합니다.
    """
    auth_service = AuthService(db)
    verification_service = VerificationService(db)

    user = auth_service.create_user(user_data)

    # 인증 이메일 발송
    verification_service.send_verification_email(user)

    return RegisterResponse(
        message="회원가입이 완료되었습니다. 이메일을 확인하여 인증을 완료해주세요.",
        email=user.email,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Login with email and password."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # 이메일 인증 확인
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account.",
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return AuthResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(**payload)

        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Get user
    user = db.query(User).filter(User.id == UUID(token_data.sub)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    """Verify user email with token.

    이메일의 인증 링크를 클릭하면 호출되는 엔드포인트입니다.
    """
    verification_service = VerificationService(db)
    success, message, user = verification_service.verify_email(request.token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return EmailVerificationResponse(success=True, message=message)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    """Resend verification email.

    인증 이메일을 재발송합니다.
    """
    auth_service = AuthService(db)
    verification_service = VerificationService(db)

    user = auth_service.get_user_by_email(request.email)

    if not user:
        # 보안상 이메일 존재 여부를 노출하지 않음
        return ResendVerificationResponse(
            success=True,
            message="등록된 이메일이라면 인증 메일이 발송됩니다."
        )

    if user.is_verified:
        return ResendVerificationResponse(
            success=False,
            message="이미 인증된 계정입니다."
        )

    success, message = verification_service.resend_verification_email(user)

    return ResendVerificationResponse(success=success, message=message)
