import uuid
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base, TimestampMixin


class AuthProvider(str, enum.Enum):
    """인증 제공자 (DB 호환성을 위해 enum 값 유지)"""
    EMAIL = "email"
    GOOGLE = "google"  # deprecated
    GITHUB = "github"  # deprecated


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    auth_provider = Column(
        SQLEnum(AuthProvider, values_callable=lambda x: [e.value for e in x]),
        default=AuthProvider.EMAIL,
        nullable=False
    )
    provider_id = Column(String(255), nullable=True)  # deprecated

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
