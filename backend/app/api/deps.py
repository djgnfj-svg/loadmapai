import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from uuid import UUID

from app.db import get_db, DatabaseConnectionError
from app.config import settings
from app.models.user import User
from app.schemas.auth import TokenPayload

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)

        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = db.query(User).filter(User.id == UUID(token_data.sub)).first()
    except OperationalError as e:
        logger.error(f"Database connection error in get_current_user: {e}")
        raise DatabaseConnectionError("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요.")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user
