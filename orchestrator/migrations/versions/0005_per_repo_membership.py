"""switch to per-repo membership: drop teams + global role, add repository_members

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-09 12:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("pipelines", "team_id")
    op.drop_column("repositories", "team_id")
    op.drop_column("repositories", "user_id")

    op.drop_table("team_members")
    op.drop_table("teams")

    op.drop_column("users", "role")
    op.execute("DROP TYPE IF EXISTS userrole")

    op.create_table(
        "repository_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repo_id", sa.String(36), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("repo_id", "user_id", name="uq_repository_members_repo_user"),
    )
    op.create_index("ix_repository_members_repo_id", "repository_members", ["repo_id"])
    op.create_index("ix_repository_members_user_id", "repository_members", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_repository_members_user_id", table_name="repository_members")
    op.drop_index("ix_repository_members_repo_id", table_name="repository_members")
    op.drop_table("repository_members")

    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'developer')")
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("admin", "developer", name="userrole", create_type=False),
            nullable=False,
            server_default="developer",
        ),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "team_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("team_id", "user_id"),
    )

    op.add_column(
        "repositories",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "repositories",
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "pipelines",
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
    )
