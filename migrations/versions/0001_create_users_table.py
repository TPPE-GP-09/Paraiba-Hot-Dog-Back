"""create users table

Revision ID: 0001_create_users_table
Revises:
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_users_table"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("admin", "caixa", "cozinha", name="user_role")


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)