"""create unidade table

Revision ID: 0003_create_unidade_table
Revises: 0002_create_endereco_table
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_create_unidade_table"
down_revision = "0002_create_endereco_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "unidades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("imagem", sa.String(length=500), nullable=True),
        sa.Column("abertura", sa.Time(), nullable=False),
        sa.Column("fechamento", sa.Time(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("endereco_id", sa.Integer(), sa.ForeignKey("enderecos.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("unidades")
