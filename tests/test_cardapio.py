import pytest

@pytest.fixture
def dados_base(cliente):
    resposta_categoria = cliente.post("/produtos/categorias", json={"nome": "Categoria Teste"})
    assert resposta_categoria.status_code == 201
    categoria = resposta_categoria.json()

    resposta_subcategoria = cliente.post("/produtos/subcategorias", json={
        "nome": "Subcategoria Teste", 
        "categoria_id": categoria["id"]
    })
    assert resposta_subcategoria.status_code == 201
    subcategoria = resposta_subcategoria.json()

    resposta_produto = cliente.post("/produtos/", json={
        "nome": "Produto Teste",
        "descricao": "Descricao",
        "imagem_url": "http://img.com/img.png",
        "ativo": True,
        "subcategoria_id": subcategoria["id"]
    })
    assert resposta_produto.status_code == 201
    produto = resposta_produto.json()

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "produto": produto
    }

@pytest.mark.parametrize(
    "rota, dados_requisicao, status_esperado",
    [
        # 201 Created: Criação com sucesso de produtos com dados válidos.
        ("/produtos/variacoes", {"tipo": "normal", "preco": 10.50}, 201),
        ("/produtos/adicionais", {"nome": "Adicional Teste", "preco": 2.50}, 201),
        
        # 422 Unprocessable Entity: Validação de erros (preços negativos, campos obrigatórios ausentes).
        ("/produtos/variacoes", {"tipo": "normal", "preco": -5.00}, 422),
        ("/produtos/adicionais", {"nome": "Invalido", "preco": -1.00}, 422),
        ("/produtos/variacoes", {"preco": 10.50}, 422),
        ("/produtos/adicionais", {"preco": 5.00}, 422),
    ]
)
def test_criar_itens(cliente, dados_base, rota, dados_requisicao, status_esperado):
    # Injetando ID do produto para manter a integridade referencial, independentemente de ser um caso de sucesso ou erro (foco da falha em outro campo)
    if "produto_id" not in dados_requisicao:
        dados_requisicao["produto_id"] = dados_base["produto"]["id"]
        
    resposta = cliente.post(rota, json=dados_requisicao)
    assert resposta.status_code == status_esperado

@pytest.mark.parametrize(
    "rota, status_esperado",
    [
        # 200 OK: Listagem e leitura de produtos, variações e adicionais.
        ("/produtos/", 200),
        ("/produtos/categorias", 200),
        ("/produtos/subcategorias", 200),
        ("/produtos/variacoes", 200),
        ("/produtos/adicionais", 200),
        ("/produtos/{produto_id}", 200),
        
        # 404 Not Found: IDs que não existem no banco.
        ("/produtos/99999", 404),
    ]
)
def test_ler_itens(cliente, dados_base, rota, status_esperado):
    if "{produto_id}" in rota:
        rota = rota.format(produto_id=dados_base["produto"]["id"])
        
    resposta = cliente.get(rota)
    assert resposta.status_code == status_esperado

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
