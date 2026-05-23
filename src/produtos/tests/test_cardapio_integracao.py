import pytest

@pytest.mark.integration
def test_relacionamentos_produto(cliente, dados_base):
    produto_id = dados_base["produto"]["id"]
    
    resposta_v = cliente.post("/produtos/variacoes", json={
        "produto_id": produto_id,
        "nome": "Combo Tradicional",
        "tipo": "combo",
        "preco": 32.90,
        "ativo": True
    })
    assert resposta_v.status_code == 201
    
    resposta_a = cliente.post("/produtos/adicionais", json={
        "produto_id": produto_id,
        "nome": "Maionese Artesanal de Ervas",
        "preco": 3.00
    })
    assert resposta_a.status_code == 201
    
    resposta_p = cliente.get(f"/produtos/{produto_id}")
    assert resposta_p.status_code == 200
    dados_produto = resposta_p.json()
    
    assert len(dados_produto["variacoes"]) > 0
    assert len(dados_produto["adicionais"]) > 0
    assert dados_produto["variacoes"][0]["tipo"] == "combo"
    assert dados_produto["variacoes"][0]["nome"] == "Combo Tradicional"
    assert dados_produto["adicionais"][0]["nome"] == "Maionese Artesanal de Ervas"


@pytest.mark.integration
def test_editar_categoria_e_subcategoria(cliente):
    resposta_categoria = cliente.post("/produtos/categorias", json={"nome": "Combos"})
    assert resposta_categoria.status_code == 201
    categoria_id = resposta_categoria.json()["id"]

    resposta_categoria_update = cliente.patch(
        f"/produtos/categorias/{categoria_id}",
        json={"nome": "Combos da Bexiga"},
    )
    assert resposta_categoria_update.status_code == 200
    assert resposta_categoria_update.json()["nome"] == "Combos da Bexiga"

    resposta_subcategoria = cliente.post(
        "/produtos/subcategorias",
        json={"nome": "Promocao", "categoria_id": categoria_id},
    )
    assert resposta_subcategoria.status_code == 201
    subcategoria_id = resposta_subcategoria.json()["id"]

    resposta_subcategoria_update = cliente.patch(
        f"/produtos/subcategorias/{subcategoria_id}",
        json={"nome": "Promocao da Bexiga"},
    )
    assert resposta_subcategoria_update.status_code == 200
    assert resposta_subcategoria_update.json()["nome"] == "Promocao da Bexiga"

    resposta_excluir_categoria_vinculada = cliente.delete(f"/produtos/categorias/{categoria_id}")
    assert resposta_excluir_categoria_vinculada.status_code == 409

    resposta_excluir_subcategoria = cliente.delete(f"/produtos/subcategorias/{subcategoria_id}")
    assert resposta_excluir_subcategoria.status_code == 204

    resposta_excluir_categoria = cliente.delete(f"/produtos/categorias/{categoria_id}")
    assert resposta_excluir_categoria.status_code == 204
