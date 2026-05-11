"""create endereco table

Revision ID: 0002_create_endereco_table
Revises: 0001_create_users_table
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_create_endereco_table"
down_revision = "0001_create_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enderecos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cep", sa.String(length=8), nullable=False),
        sa.Column("logradouro", sa.String(length=255), nullable=False),
        sa.Column("numero", sa.String(length=10), nullable=True),
        sa.Column("complemento", sa.String(length=255), nullable=True),
        sa.Column("bairro", sa.String(length=255), nullable=False),
        sa.Column("cidade", sa.String(length=255), nullable=False),
        sa.Column("estado", sa.String(length=2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("enderecos")
