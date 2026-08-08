"""Secure password reset state.

Revision ID: 8c761ea22d11
Revises: 309ffcd962c0
Create Date: 2026-08-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c761ea22d11"
down_revision: Union[str, Sequence[str], None] = "309ffcd962c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "password_reset_otp",
        existing_type=sa.String(length=6),
        type_=sa.String(length=64),
        existing_nullable=True,
    )
    op.add_column(
        "users",
        sa.Column("password_reset_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("password_reset_token", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("password_reset_token_expires", sa.DateTime(timezone=True), nullable=True),
    )
    op.drop_column("users", "is_password_reset_authorized")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_password_reset_authorized",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.drop_column("users", "password_reset_token_expires")
    op.drop_column("users", "password_reset_token")
    op.drop_column("users", "password_reset_attempts")
    op.alter_column(
        "users",
        "password_reset_otp",
        existing_type=sa.String(length=64),
        type_=sa.String(length=6),
        existing_nullable=True,
    )
