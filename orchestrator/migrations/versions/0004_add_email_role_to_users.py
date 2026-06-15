"""add email and role to users

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-09 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(256), nullable=True))
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'developer')")
    op.add_column("users", sa.Column(
        "role",
        sa.Enum("admin", "developer", name="userrole", create_type=False),
        nullable=False,
        server_default="developer",
    ))


def downgrade() -> None:
    op.drop_column("users", "role")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "email")
    op.execute("DROP TYPE IF EXISTS userrole")
