from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: int
    type: str  # access or refresh


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterResponse(BaseModel):
    """회원가입 응답 (이메일 인증 필요)"""
    message: str
    email: str


class EmailVerificationRequest(BaseModel):
    """이메일 인증 요청"""
    token: str


class EmailVerificationResponse(BaseModel):
    """이메일 인증 응답"""
    success: bool
    message: str


class ResendVerificationRequest(BaseModel):
    """인증 이메일 재발송 요청"""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """인증 이메일 재발송 응답"""
    success: bool
    message: str
