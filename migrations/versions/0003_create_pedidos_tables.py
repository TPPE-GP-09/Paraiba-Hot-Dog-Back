"""create pedidos tables

Revision ID: 0003_create_pedidos_tables
Revises: 104214f51d04
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_create_pedidos_tables"
down_revision = "104214f51d04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE status_pedido AS ENUM ('preparando', 'entregue', 'cancelado');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )

    op.create_table(
        "mesas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("unidade_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["unidade_id"], ["unidades.id"]),
    )

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("mesa_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "preparando", "entregue", "cancelado",
                name="status_pedido",
                create_type=False,
            ),
            nullable=False,
            server_default="preparando",
        ),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["mesa_id"], ["mesas.id"]),
    )

    op.create_table(
        "itens_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
    )

    op.create_table(
        "adicionais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_pedido_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["item_pedido_id"], ["itens_pedido.id"]),
    )


def downgrade() -> None:
    op.drop_table("adicionais")
    op.drop_table("itens_pedido")
    op.drop_table("pedidos")
    op.drop_table("mesas")
    op.execute("DROP TYPE IF EXISTS status_pedido")
