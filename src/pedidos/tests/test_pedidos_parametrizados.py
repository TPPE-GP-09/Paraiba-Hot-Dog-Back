import pytest


@pytest.mark.parametrize(
    "payload, status_esperado",
    [
        (
            {
                "unidade_id": 999,
                "nome_comanda": "Unidade inexistente",
                "cliente_id": None,
                "itens": [],
            },
            404,
        ),
        (
            {
                "unidade_id": 1,
                "nome_comanda": "",
                "cliente_id": None,
                "itens": [],
            },
            422,
        ),
    ],
)
def test_validacoes_criar_pedido(cliente, cardapio_base, payload, status_esperado):
    if payload["unidade_id"] == 1:
        payload["unidade_id"] = cardapio_base["unidade"].id

    resposta = cliente.post("/pedidos/", json=payload)
    assert resposta.status_code == status_esperado


@pytest.mark.parametrize(
    "status_cozinha, status_esperado",
    [
        ("preparando", 200),
        ("entregue", 200),
        ("cancelado", 400),
    ],
)
def test_status_permitidos_na_cozinha(cliente, cardapio_base, status_cozinha, status_esperado):
    resposta_pedido = cliente.post(
        "/pedidos/",
        json={
            "unidade_id": cardapio_base["unidade"].id,
            "nome_comanda": "Daniel",
            "cliente_id": None,
            "itens": [
                {
                    "produto_variacao_id": cardapio_base["variacao"].id,
                    "quantidade": 1,
                    "observacao": "Sem milho",
                    "adicional_ids": [cardapio_base["adicionais"][0].id],
                }
            ],
        },
    )
    assert resposta_pedido.status_code == 201
    pedido = resposta_pedido.json()

    resposta_status = cliente.patch(
        "/pedidos/cozinha/status",
        json={
            "pedido_id": pedido["id"],
            "lote": 1,
            "produto_variacao_id": cardapio_base["variacao"].id,
            "observacao": "Sem milho",
            "adicional_ids": [cardapio_base["adicionais"][0].id],
            "status": status_cozinha,
        },
    )
    assert resposta_status.status_code == status_esperado


@pytest.mark.parametrize(
    "forma_pagamento",
    ["pix", "credito", "debito", "dinheiro"],
)
def test_formas_pagamento(cliente, cardapio_base, forma_pagamento):
    resposta_pedido = cliente.post(
        "/pedidos/",
        json={
            "unidade_id": cardapio_base["unidade"].id,
            "nome_comanda": "Daniel",
            "cliente_id": cardapio_base["cliente"].id,
            "itens": [
                {
                    "produto_variacao_id": cardapio_base["variacao"].id,
                    "quantidade": 1,
                    "observacao": None,
                    "adicional_ids": [],
                }
            ],
        },
    )
    assert resposta_pedido.status_code == 201

    resposta_pagamento = cliente.post(
        f"/pedidos/{resposta_pedido.json()['id']}/finalizar",
        json={"forma_pagamento": forma_pagamento},
    )
    assert resposta_pagamento.status_code == 200
    assert resposta_pagamento.json()["status"] == "pago"
    assert resposta_pagamento.json()["forma_pagamento"] == forma_pagamento
