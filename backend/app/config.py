from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "LoadmapAI"
    debug: bool = False

    # Database
    database_url: str = "postgresql://loadmap:loadmap123@db:5432/loadmap_db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Anthropic
    anthropic_api_key: str = ""

    # OAuth - Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # OAuth - GitHub
    github_client_id: str = ""
    github_client_secret: str = ""

    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
