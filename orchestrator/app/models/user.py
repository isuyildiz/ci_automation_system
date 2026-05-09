import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    developer = "developer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.developer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
