import pytest

@pytest.mark.integration
def test_relacionamentos_produto(cliente, dados_base):
    produto_id = dados_base["produto"]["id"]
    
    resposta_v = cliente.post("/produtos/variacoes", json={
        "produto_id": produto_id,
        "tipo": "combo",
        "preco": 15.00,
        "preco_combo": 20.00,
        "label_combo": "Combo Master"
    })
    assert resposta_v.status_code == 201
    
    resposta_a = cliente.post("/produtos/adicionais", json={
        "produto_id": produto_id,
        "nome": "Bacon",
        "preco": 3.00
    })
    assert resposta_a.status_code == 201
    
    resposta_p = cliente.get(f"/produtos/{produto_id}")
    assert resposta_p.status_code == 200
    dados_produto = resposta_p.json()
    
    assert len(dados_produto["variacoes"]) > 0
    assert len(dados_produto["adicionais"]) > 0
    assert dados_produto["variacoes"][0]["tipo"] == "combo"
    assert dados_produto["adicionais"][0]["nome"] == "Bacon"
