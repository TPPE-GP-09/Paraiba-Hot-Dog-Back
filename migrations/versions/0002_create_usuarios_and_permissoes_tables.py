"""create usuarios and permissoes tables

Revision ID: 0002_usuarios_permissoes
Revises: 0001_create_users_table
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_usuarios_permissoes"
down_revision = "0001_create_users_table"
branch_labels = None
depends_on = None


funcao_usuario = postgresql.ENUM(
    "adiministrador",
    "caixa",
    "cozinha",
    name="funcao_usuario",
    create_type=False,
)

tipo_permissao = postgresql.ENUM(
    "anotar_pedidos",
    "cozinha",
    "dasbord",
    "configuracoes",
    name="tipo_permissao",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE funcao_usuario AS ENUM ('adiministrador', 'caixa', 'cozinha');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE tipo_permissao AS ENUM ('anotar_pedidos', 'cozinha', 'dasbord', 'configuracoes');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )

    op.create_table(
        "permissoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", tipo_permissao, nullable=False),
        sa.UniqueConstraint("nome", name="uq_permissoes_nome"),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha", sa.String(length=255), nullable=False),
        sa.Column("funcao", funcao_usuario, nullable=False, server_default="caixa"),
        sa.Column("permissao_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["permissao_id"], ["permissoes.id"]),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("permissoes")
    tipo_permissao.drop(op.get_bind(), checkfirst=True)
    funcao_usuario.drop(op.get_bind(), checkfirst=True)
