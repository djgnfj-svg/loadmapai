from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "LoadmapAI"
    debug: bool = False

    # Database
    database_url: str = "postgresql://loadmap:loadmap123@db:5432/loadmap_db"

    # Security - SECRET_KEY는 반드시 환경변수로 설정해야 함
    secret_key: str

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY must be set via environment variable. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Anthropic
    anthropic_api_key: str = ""

    # URLs
    frontend_url: str = "http://localhost:3000"

    # Beta limits (베타 기간 제한)
    beta_daily_roadmap_limit: int = 1  # 하루 로드맵 생성 제한 (0=무제한)

    # Email (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""  # Gmail 주소
    smtp_password: str = ""  # Gmail 앱 비밀번호
    smtp_from_name: str = "LoadmapAI"
    email_verification_expire_hours: int = 24

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/oauth/google/callback"

    # Sentry (에러 모니터링)
    sentry_dsn: str = ""  # 프로덕션에서 설정

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
