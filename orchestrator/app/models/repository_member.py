import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RepoRole(str, enum.Enum):
    owner = "owner"
    member = "member"


class RepositoryMember(Base):
    __tablename__ = "repository_members"
    __table_args__ = (UniqueConstraint("repo_id", "user_id", name="uq_repository_members_repo_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_id: Mapped[str] = mapped_column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default=RepoRole.member.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    repository: Mapped["Repository"] = relationship("Repository", back_populates="members")
    user: Mapped["User"] = relationship("User")
