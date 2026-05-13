"""update schema: categorias, subcategorias, produto_variacoes, clientes, formas_pagamento, pedido_pagamento

Revision ID: 0004_update_schema
Revises: 0003_create_pedidos_tables
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_update_schema"
down_revision = "0003_create_pedidos_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Novos enums
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipo_variacao AS ENUM ('normal', 'combo');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE status_mesa AS ENUM ('livre', 'ocupada');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)

    # Novas tabelas independentes
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(100), nullable=False),
    )

    op.create_table(
        "subcategorias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
    )

    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("pontos_fidelidade", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "formas_pagamento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(50), nullable=False, unique=True),
    )

    # Atualiza produtos: remove colunas antigas, adiciona subcategoria_id
    op.drop_column("produtos", "preco")
    op.drop_column("produtos", "preco_combo")
    op.drop_column("produtos", "categoria")
    op.drop_column("produtos", "esta_ativo")
    op.drop_column("produtos", "observacao")
    op.drop_column("produtos", "imagem")
    op.drop_column("produtos", "unidade_id")
    op.add_column("produtos", sa.Column("imagem_url", sa.String(500), nullable=True))
    op.add_column("produtos", sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("produtos", sa.Column("subcategoria_id", sa.Integer(), nullable=False, server_default="1"))
    op.create_foreign_key("fk_produtos_subcategoria_id", "produtos", "subcategorias", ["subcategoria_id"], ["id"])
    # Remove server_default após aplicar
    op.alter_column("produtos", "subcategoria_id", server_default=None)
    op.alter_column("produtos", "descricao", type_=sa.Text())

    # Nova tabela produto_variacoes
    op.create_table(
        "produto_variacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            postgresql.ENUM("normal", "combo", name="tipo_variacao", create_type=False),
            nullable=False,
        ),
        sa.Column("preco", sa.Numeric(10, 2), nullable=False),
        sa.Column("preco_combo", sa.Numeric(10, 2), nullable=True),
        sa.Column("label_combo", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
    )

    # Atualiza mesas: remove unidade_id, adiciona status
    op.drop_constraint("mesas_unidade_id_fkey", "mesas", type_="foreignkey")
    op.drop_column("mesas", "unidade_id")
    op.add_column(
        "mesas",
        sa.Column(
            "status",
            postgresql.ENUM("livre", "ocupada", name="status_mesa", create_type=False),
            nullable=False,
            server_default="livre",
        ),
    )

    # Atualiza pedidos: renomeia criado_em → hora, adiciona cliente_id, remove observacao
    op.alter_column("pedidos", "criado_em", new_column_name="hora")
    op.drop_column("pedidos", "observacao")
    op.add_column("pedidos", sa.Column("cliente_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_pedidos_cliente_id", "pedidos", "clientes", ["cliente_id"], ["id"])

    # Atualiza itens_pedido: remove produto_id, adiciona variacao_id, observacao, preco_unitario
    op.drop_constraint("itens_pedido_produto_id_fkey", "itens_pedido", type_="foreignkey")
    op.drop_column("itens_pedido", "produto_id")
    op.add_column("itens_pedido", sa.Column("variacao_id", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("itens_pedido", sa.Column("observacao", sa.Text(), nullable=True))
    op.add_column("itens_pedido", sa.Column("preco_unitario", sa.Numeric(10, 2), nullable=False, server_default="0"))
    op.create_foreign_key("fk_itens_pedido_variacao_id", "itens_pedido", "produto_variacoes", ["variacao_id"], ["id"])
    op.alter_column("itens_pedido", "variacao_id", server_default=None)
    op.alter_column("itens_pedido", "preco_unitario", server_default=None)

    # Nova tabela pedido_pagamento
    op.create_table(
        "pedido_pagamento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("forma_pagamento_id", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("taxas", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.ForeignKeyConstraint(["forma_pagamento_id"], ["formas_pagamento.id"]),
    )


def downgrade() -> None:
    op.drop_table("pedido_pagamento")

    op.drop_constraint("fk_itens_pedido_variacao_id", "itens_pedido", type_="foreignkey")
    op.drop_column("itens_pedido", "preco_unitario")
    op.drop_column("itens_pedido", "observacao")
    op.drop_column("itens_pedido", "variacao_id")
    op.add_column("itens_pedido", sa.Column("produto_id", sa.Integer(), nullable=False, server_default="1"))
    op.create_foreign_key("itens_pedido_produto_id_fkey", "itens_pedido", "produtos", ["produto_id"], ["id"])
    op.alter_column("itens_pedido", "produto_id", server_default=None)

    op.drop_constraint("fk_pedidos_cliente_id", "pedidos", type_="foreignkey")
    op.drop_column("pedidos", "cliente_id")
    op.add_column("pedidos", sa.Column("observacao", sa.Text(), nullable=True))
    op.alter_column("pedidos", "hora", new_column_name="criado_em")

    op.drop_column("mesas", "status")
    op.add_column("mesas", sa.Column("unidade_id", sa.Integer(), nullable=False, server_default="1"))
    op.create_foreign_key("mesas_unidade_id_fkey", "mesas", "unidades", ["unidade_id"], ["id"])
    op.alter_column("mesas", "unidade_id", server_default=None)

    op.drop_table("produto_variacoes")

    op.drop_constraint("fk_produtos_subcategoria_id", "produtos", type_="foreignkey")
    op.drop_column("produtos", "subcategoria_id")
    op.drop_column("produtos", "ativo")
    op.drop_column("produtos", "imagem_url")
    op.add_column("produtos", sa.Column("unidade_id", sa.Integer(), nullable=True))
    op.add_column("produtos", sa.Column("imagem", sa.String(500), nullable=True))
    op.add_column("produtos", sa.Column("observacao", sa.Text(), nullable=True))
    op.add_column("produtos", sa.Column("esta_ativo", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("produtos", sa.Column("categoria", sa.String(100), nullable=False, server_default=""))
    op.add_column("produtos", sa.Column("preco_combo", sa.Float(), nullable=True))
    op.add_column("produtos", sa.Column("preco", sa.Float(), nullable=False, server_default="0"))

    op.drop_table("formas_pagamento")
    op.drop_table("clientes")
    op.drop_table("subcategorias")
    op.drop_table("categorias")

    op.execute("DROP TYPE IF EXISTS status_mesa")
    op.execute("DROP TYPE IF EXISTS tipo_variacao")
