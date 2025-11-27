from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import UserCreate, UserLogin, AuthResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user with email and password."""
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return AuthResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
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

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return AuthResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )
