"""Custom exceptions and error handlers for the application."""

from typing import Any, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for the application."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str = "Resource", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or f"{resource}을(를) 찾을 수 없습니다.",
            error_code="NOT_FOUND",
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, detail: str = "인증이 필요합니다."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, detail: str = "접근 권한이 없습니다."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
        )


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, detail: str = "잘못된 요청입니다."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
        )


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate resource)."""

    def __init__(self, detail: str = "이미 존재하는 리소스입니다."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
        )


class AIServiceException(AppException):
    """AI service related exception."""

    def __init__(self, detail: str = "AI 서비스 처리 중 오류가 발생했습니다."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="AI_SERVICE_ERROR",
        )


class ValidationException(AppException):
    """Validation error exception."""

    def __init__(self, detail: str = "입력값이 올바르지 않습니다."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


# ============ Resource Specific Exceptions ============

class UserNotFoundException(NotFoundException):
    """Raised when a user is not found."""

    def __init__(self, user_id: str = None, email: str = None):
        identifier = email or user_id or "알 수 없음"
        super().__init__(resource="사용자", detail=f"사용자({identifier})를 찾을 수 없습니다.")


class RoadmapNotFoundException(NotFoundException):
    """Raised when a roadmap is not found."""

    def __init__(self, roadmap_id: str = None):
        super().__init__(resource="로드맵", detail="로드맵을 찾을 수 없습니다.")
