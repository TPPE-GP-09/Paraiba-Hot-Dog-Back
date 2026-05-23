import pytest


@pytest.mark.integration
def test_criar_pagar_e_manter_item_na_cozinha(cliente, cardapio_base):
    payload = {
        "unidade_id": cardapio_base["unidade"].id,
        "nome_comanda": "Daniel",
        "cliente_id": cardapio_base["cliente"].id,
        "observacao": "Pago no caixa",
        "itens": [
            {
                "produto_variacao_id": cardapio_base["variacao"].id,
                "quantidade": 2,
                "observacao": "Sem milho",
                "adicional_ids": [adicional.id for adicional in cardapio_base["adicionais"]],
            }
        ],
    }

    resposta_pedido = cliente.post("/pedidos/", json=payload)
    assert resposta_pedido.status_code == 201
    pedido = resposta_pedido.json()
    assert pedido["status"] == "aberto"
    assert pedido["total"] == "51.80"
    assert pedido["itens"][0]["produto_nome"] == "Tradicional"
    assert pedido["itens"][0]["produto_variacao_nome"] == "Tradicional"

    resposta_pagamento = cliente.post(
        f"/pedidos/{pedido['id']}/finalizar",
        json={"forma_pagamento": "pix"},
    )
    assert resposta_pagamento.status_code == 200
    pedido_pago = resposta_pagamento.json()
    assert pedido_pago["status"] == "pago"
    assert pedido_pago["pontos_fidelidade_creditados"] is True

    resposta_cozinha = cliente.get(
        f"/pedidos/cozinha?unidade_id={cardapio_base['unidade'].id}"
    )
    assert resposta_cozinha.status_code == 200
    cozinha = resposta_cozinha.json()
    assert len(cozinha) == 1
    assert cozinha[0]["pedido_id"] == pedido["id"]
    assert cozinha[0]["nome_comanda"] == "Daniel"
    assert cozinha[0]["quantidade"] == 2

    resposta_cliente = cliente.get(f"/clientes/{cardapio_base['cliente'].id}")
    assert resposta_cliente.status_code == 200
    assert resposta_cliente.json()["pontos_fidelidade"] == 2


@pytest.mark.integration
def test_cancelamento_parcial_divide_item(cliente, cardapio_base):
    resposta_pedido = cliente.post(
        "/pedidos/",
        json={
            "unidade_id": cardapio_base["unidade"].id,
            "nome_comanda": "Maria",
            "cliente_id": None,
            "observacao": None,
            "itens": [
                {
                    "produto_variacao_id": cardapio_base["variacao"].id,
                    "quantidade": 4,
                    "observacao": None,
                    "adicional_ids": [],
                }
            ],
        },
    )
    assert resposta_pedido.status_code == 201
    pedido = resposta_pedido.json()
    item_id = pedido["itens"][0]["id"]

    resposta_cancelar = cliente.post(
        f"/pedidos/itens/{item_id}/cancelar",
        json={
            "quantidade": 1,
            "motivo_cancelamento": "Cliente desistiu de uma unidade",
        },
    )
    assert resposta_cancelar.status_code == 200
    itens = resposta_cancelar.json()["itens"]

    item_ativo = next(item for item in itens if item["status"] == "aberto")
    item_cancelado = next(item for item in itens if item["status"] == "cancelado")
    assert item_ativo["quantidade"] == 3
    assert item_cancelado["quantidade"] == 1
    assert item_cancelado["motivo_cancelamento"] == "Cliente desistiu de uma unidade"
