"""이메일 인증 토큰 서비스"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.services.email_service import email_service


class VerificationService:
    """이메일 인증 토큰 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def create_verification_token(self, user: User) -> EmailVerificationToken:
        """새 인증 토큰 생성

        기존 미사용 토큰은 무효화하고 새 토큰을 생성합니다.

        Args:
            user: 인증 토큰을 생성할 사용자

        Returns:
            생성된 인증 토큰 객체
        """
        # 기존 미사용 토큰 무효화
        self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.is_used == False  # noqa: E712
        ).update({"is_used": True})

        # 새 토큰 생성
        token = EmailVerificationToken(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(
                hours=settings.email_verification_expire_hours
            )
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_verification_token(self, token: str) -> Optional[EmailVerificationToken]:
        """토큰 문자열로 인증 토큰 조회

        Args:
            token: 토큰 문자열

        Returns:
            인증 토큰 객체 또는 None
        """
        return self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token
        ).first()

    def verify_email(self, token: str) -> Tuple[bool, str, Optional[User]]:
        """이메일 인증 처리

        Args:
            token: 인증 토큰 문자열

        Returns:
            (성공 여부, 메시지, 사용자 객체)
        """
        verification = self.get_verification_token(token)

        if not verification:
            return False, "유효하지 않은 인증 링크입니다.", None

        if verification.is_used:
            return False, "이미 사용된 인증 링크입니다.", None

        if verification.is_expired:
            return False, "만료된 인증 링크입니다. 새 인증 이메일을 요청해주세요.", None

        # 토큰 사용 처리
        verification.is_used = True

        # 사용자 인증 완료 처리
        user = self.db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.is_verified = True

        self.db.commit()

        return True, "이메일 인증이 완료되었습니다.", user

    def send_verification_email(self, user: User) -> bool:
        """인증 이메일 발송

        새 인증 토큰을 생성하고 이메일을 발송합니다.

        Args:
            user: 이메일을 발송할 사용자

        Returns:
            발송 성공 여부
        """
        token = self.create_verification_token(user)
        verification_link = f"{settings.frontend_url}/verify-email?token={token.token}"

        return email_service.send_verification_email(
            to_email=user.email,
            user_name=user.name,
            verification_link=verification_link
        )

    def resend_verification_email(self, user: User) -> Tuple[bool, str]:
        """인증 이메일 재발송

        Args:
            user: 이메일을 재발송할 사용자

        Returns:
            (성공 여부, 메시지)
        """
        if user.is_verified:
            return False, "이미 인증된 계정입니다."

        success = self.send_verification_email(user)
        if success:
            return True, "인증 이메일이 발송되었습니다."
        return False, "이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요."
