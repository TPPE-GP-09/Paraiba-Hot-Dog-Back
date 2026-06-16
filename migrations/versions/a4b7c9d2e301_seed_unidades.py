"""seed unidades

Revision ID: a4b7c9d2e301
Revises: 7e2a9c4d6f10
Create Date: 2026-05-23 14:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "a4b7c9d2e301"
down_revision = "7e2a9c4d6f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    unidades = [
        {
            "nome": "Unidade Aguas Claras (Avenida Jequitiba)",
            "cep": "70297400",
            "logradouro": "Av. Jequitiba Praca Tangara",
            "numero": None,
            "complemento": None,
            "bairro": "Aguas Claras",
            "cidade": "Brasilia",
            "estado": "DF",
            "abertura": "18:00",
            "fechamento": "23:00",
            "descricao": "Unidade da Avenida Jequitiba em Aguas Claras.",
            "imagem": "/uploads/unidades/unidade-jequitiba.jpeg",
        },
        {
            "nome": "Unidade Aguas Claras (Avenida das Araucarias)",
            "cep": "70297400",
            "logradouro": "Av. das Araucarias",
            "numero": "1395",
            "complemento": None,
            "bairro": "Aguas Claras",
            "cidade": "Brasilia",
            "estado": "DF",
            "abertura": "17:00",
            "fechamento": "23:00",
            "descricao": "Unidade da Avenida das Araucarias em Aguas Claras.",
            "imagem": "/uploads/unidades/unidade-araucarias.jpeg",
        },
    ]

    for unidade in unidades:
        exists = conn.execute(
            sa.text("SELECT 1 FROM unidades WHERE nome = :nome"),
            {"nome": unidade["nome"]},
        ).first()
        if exists:
            continue

        endereco_id = conn.execute(
            sa.text(
                """
                INSERT INTO enderecos
                    (cep, logradouro, numero, complemento, bairro, cidade, estado)
                VALUES
                    (:cep, :logradouro, :numero, :complemento, :bairro, :cidade, :estado)
                RETURNING id
                """
            ),
            unidade,
        ).scalar_one()

        conn.execute(
            sa.text(
                """
                INSERT INTO unidades
                    (nome, abertura, fechamento, descricao, imagem, endereco_id)
                VALUES
                    (:nome, :abertura, :fechamento, :descricao, :imagem, :endereco_id)
                """
            ),
            {**unidade, "endereco_id": endereco_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    nomes = ["Unidade Aguas Claras (Avenida Jequitiba)", "Unidade Aguas Claras (Avenida das Araucarias)"]
    endereco_ids = [
        row[0]
        for row in conn.execute(
            sa.text("SELECT endereco_id FROM unidades WHERE nome = ANY(:nomes)"),
            {"nomes": nomes},
        )
    ]
    conn.execute(sa.text("DELETE FROM unidades WHERE nome = ANY(:nomes)"), {"nomes": nomes})
    if endereco_ids:
        conn.execute(sa.text("DELETE FROM enderecos WHERE id = ANY(:ids)"), {"ids": endereco_ids})
