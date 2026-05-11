"""add unidade_id to usuarios

Revision ID: 0003_add_unidade_id
Revises: 0002_usuarios_permissoes
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_add_unidade_id"
down_revision = "0002_usuarios_permissoes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("unidade_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "unidade_id")
