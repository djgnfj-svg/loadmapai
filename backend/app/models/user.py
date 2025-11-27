import uuid
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # nullable for OAuth users
    avatar_url = Column(String(500), nullable=True)

    # Auth provider info
    auth_provider = Column(
        SQLEnum(AuthProvider),
        default=AuthProvider.EMAIL,
        nullable=False
    )
    provider_id = Column(String(255), nullable=True)  # OAuth provider user ID

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships (to be added)
    # roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
