import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from typing import Generator

from app.config import settings

logger = logging.getLogger(__name__)

# Check if we're in testing mode
is_testing = os.getenv("TESTING", "false").lower() == "true"

# Configure engine based on database type
if is_testing or settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    )
else:
    # Supabase connection pooler 최적화 설정
    # Session mode에서는 pool_size 제한이 있으므로 보수적으로 설정
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # 연결 유효성 검사
        pool_size=5,  # 기본 연결 수 (Supabase free tier 고려)
        max_overflow=5,  # 추가 연결 허용 수
        pool_timeout=30,  # 연결 대기 타임아웃 (초)
        pool_recycle=1800,  # 30분마다 연결 재활용
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseConnectionError(Exception):
    """Database connection error."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션을 생성하고 반환합니다.
    연결 실패 시 DatabaseConnectionError를 발생시킵니다.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요.")
    finally:
        db.close()
