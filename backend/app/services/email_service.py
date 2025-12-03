"""이메일 발송 서비스 (SMTP)"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP를 사용한 이메일 발송 서비스"""

    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_name = settings.smtp_from_name

    @property
    def is_configured(self) -> bool:
        """SMTP 설정이 완료되었는지 확인"""
        return bool(self.user and self.password)

    def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        verification_link: str
    ) -> bool:
        """인증 이메일 발송"""
        if not self.is_configured:
            logger.warning("SMTP not configured, skipping email send")
            logger.info(f"[DEV] Verification link for {to_email}: {verification_link}")
            return True

        subject = "[LoadmapAI] 이메일 인증을 완료해주세요"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <div style="text-align: center; margin-bottom: 32px;">
                <h1 style="color: #7c3aed; margin: 0; font-size: 28px;">LoadmapAI</h1>
            </div>

            <h2 style="color: #1a1a1a; margin: 0 0 16px 0; font-size: 24px;">안녕하세요, {user_name}님!</h2>

            <p style="margin: 0 0 16px 0; color: #4b5563;">LoadmapAI에 가입해 주셔서 감사합니다.</p>
            <p style="margin: 0 0 16px 0; color: #4b5563;">아래 버튼을 클릭하여 이메일 인증을 완료해주세요:</p>

            <div style="text-align: center;">
                <a href="{verification_link}" style="display: inline-block; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; margin: 24px 0;">이메일 인증하기</a>
            </div>

            <p style="font-size: 14px; color: #6b7280;">
                버튼이 작동하지 않는 경우, 아래 링크를 브라우저에 직접 붙여넣으세요:
            </p>
            <div style="word-break: break-all; color: #6b7280; font-size: 14px; background: #f3f4f6; padding: 12px; border-radius: 6px; margin: 16px 0;">{verification_link}</div>

            <div style="background: #fef3c7; color: #92400e; padding: 12px 16px; border-radius: 6px; font-size: 14px; margin-top: 24px;">
                이 링크는 24시간 동안만 유효합니다.
            </div>

            <div style="color: #9ca3af; font-size: 13px; margin-top: 32px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
                <p style="margin: 0 0 8px 0;">본인이 가입하지 않으셨다면 이 이메일을 무시해주세요.</p>
                <p style="margin: 0;">&copy; 2024 LoadmapAI. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.user}>"
            msg["To"] = to_email

            # HTML 파트 추가
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # SMTP 연결 및 발송
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, to_email, msg.as_string())

            logger.info(f"Verification email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False


# 싱글톤 인스턴스
email_service = EmailService()
