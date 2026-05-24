"""Testes unitarios diretos para o repository de produtos."""

from datetime import time
from decimal import Decimal
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.produtos import repository
from src.produtos.model import Categoria, Produto, ProdutoAdicional, ProdutoVariacao, Subcategoria, TipoVariacao
from src.produtos.schema import (
    CategoriaCreate,
    CategoriaUpdate,
    ProdutoAdicionalCreate,
    ProdutoAdicionalUpdate,
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoVariacaoCreate,
    ProdutoVariacaoUpdate,
    SubcategoriaCreate,
    SubcategoriaUpdate,
)
from src.unidades.model import Endereco, Unidade


TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class FakeIntegrityOrig:
    """Origem fake para construir IntegrityError com mensagem controlada."""

    def __str__(self):
        """Retorna a mensagem do erro original."""
        return "erro de integridade"


class FakeQuery:
    """Query fake minima para cobrir encadeamentos do repository."""

    def __init__(self, items=None, first_item=None):
        """Configura itens retornados por all e first."""
        self.items = items or []
        self.first_item = first_item
        self.filtered = False
        self.offset_value = None
        self.limit_value = None

    def filter(self, *_args):
        """Registra filtro e mantem a query encadeavel."""
        self.filtered = True
        return self

    def offset(self, value):
        """Registra offset e mantem a query encadeavel."""
        self.offset_value = value
        return self

    def limit(self, value):
        """Registra limit e mantem a query encadeavel."""
        self.limit_value = value
        return self

    def all(self):
        """Retorna a lista configurada."""
        return self.items

    def first(self):
        """Retorna o primeiro item configurado."""
        return self.first_item


def integrity_error() -> IntegrityError:
    """Cria um IntegrityError previsivel para os testes."""
    return IntegrityError("statement", "params", FakeIntegrityOrig())


@pytest.fixture(name="db")
def fixture_db():
    """Cria uma sessao SQLite em memoria para cada teste."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def criar_base(db):
    """Cria categoria, subcategoria, unidade e produto base."""
    endereco = Endereco(
        cep="58000000",
        logradouro="Rua Teste",
        bairro="Centro",
        cidade="Joao Pessoa",
        estado="PB",
    )
    unidade = Unidade(
        nome="Unidade Centro",
        abertura=time(10, 0),
        fechamento=time(22, 0),
        endereco=endereco,
    )
    categoria = Categoria(nome="Hot-Dog")
    subcategoria = Subcategoria(nome="Tradicionais", categoria=categoria)
    produto = Produto(
        nome="Tradicional",
        descricao="Pao e salsicha",
        ativo=True,
        pontos_fidelidade_por_unidade=1,
        disponivel_todas_unidades=True,
        subcategoria=subcategoria,
    )
    db.add_all([endereco, unidade, categoria, subcategoria, produto])
    db.commit()
    return categoria, subcategoria, unidade, produto


def test_categorias_fluxo_feliz_e_validacoes(db):
    """Cobre listagem, criacao, atualizacao, busca e exclusao de categorias."""
    categoria = repository.criar_categoria(db, CategoriaCreate(nome="Bebidas"))

    assert repository.listar_categorias(db)[0].nome == "Bebidas"
    assert repository.obter_categoria(db, categoria.id) == categoria

    atualizada = repository.atualizar_categoria(
        db,
        categoria.id,
        CategoriaUpdate(nome="Bebidas Geladas"),
    )
    assert atualizada.nome == "Bebidas Geladas"

    repository.excluir_categoria(db, categoria.id)
    with pytest.raises(HTTPException) as exc_info:
        repository.obter_categoria(db, categoria.id)
    assert exc_info.value.status_code == 404


def test_categorias_erros_de_integridade(monkeypatch):
    """Cobre erros de commit nas operacoes de categoria."""
    db = Mock()
    db.commit.side_effect = integrity_error()

    with pytest.raises(HTTPException) as exc_info:
        repository.criar_categoria(db, CategoriaCreate(nome="Hot-Dog"))
    assert exc_info.value.status_code == 409
    db.rollback.assert_called()

    monkeypatch.setattr(repository, "obter_categoria", lambda _db, _id: Categoria(id=1, nome="Hot-Dog"))
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_categoria(db, 1, CategoriaUpdate(nome="Novo"))
    assert exc_info.value.detail == "Erro ao atualizar categoria"

    categoria = Categoria(id=1, nome="Hot-Dog")
    categoria.subcategorias = []
    monkeypatch.setattr(repository, "obter_categoria", lambda _db, _id: categoria)
    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_categoria(db, 1)
    assert exc_info.value.detail == "Erro ao excluir categoria"


def test_excluir_categoria_com_subcategoria_vinculada(db):
    """Garante conflito ao excluir categoria com subcategorias."""
    categoria, _, _, _ = criar_base(db)

    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_categoria(db, categoria.id)

    assert exc_info.value.status_code == 409


def test_subcategorias_fluxo_feliz_e_validacoes(db):
    """Cobre listagem, criacao, atualizacao, busca e exclusao de subcategorias."""
    categoria = repository.criar_categoria(db, CategoriaCreate(nome="Combos"))
    subcategoria = repository.criar_subcategoria(
        db,
        SubcategoriaCreate(nome="Promocoes", categoria_id=categoria.id),
    )

    assert repository.listar_subcategorias(db)[0].nome == "Promocoes"
    assert repository.obter_subcategoria(db, subcategoria.id) == subcategoria

    atualizada = repository.atualizar_subcategoria(
        db,
        subcategoria.id,
        SubcategoriaUpdate(nome="Promocoes Especiais", categoria_id=categoria.id),
    )
    assert atualizada.nome == "Promocoes Especiais"

    repository.excluir_subcategoria(db, subcategoria.id)
    with pytest.raises(HTTPException) as exc_info:
        repository.obter_subcategoria(db, subcategoria.id)
    assert exc_info.value.status_code == 404


def test_subcategorias_erros(monkeypatch):
    """Cobre erros de categoria ausente e integridade em subcategorias."""
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        repository.criar_subcategoria(db, SubcategoriaCreate(nome="Molhos", categoria_id=99))
    assert exc_info.value.detail == "Categoria nao encontrada"

    db.get.return_value = Categoria(id=1, nome="Hot-Dog")
    db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_subcategoria(db, SubcategoriaCreate(nome="Molhos", categoria_id=1))
    assert exc_info.value.detail == "Erro ao criar subcategoria"

    subcategoria = Subcategoria(id=1, nome="Molhos", categoria_id=1)
    monkeypatch.setattr(repository, "obter_subcategoria", lambda _db, _id: subcategoria)
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_subcategoria(db, 1, SubcategoriaUpdate(categoria_id=2))
    assert exc_info.value.detail == "Categoria nao encontrada"

    db.get.return_value = Categoria(id=2, nome="Combos")
    db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_subcategoria(db, 1, SubcategoriaUpdate(nome="Novo", categoria_id=2))
    assert exc_info.value.detail == "Erro ao atualizar subcategoria"

    subcategoria.produtos = []
    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_subcategoria(db, 1)
    assert exc_info.value.detail == "Erro ao excluir subcategoria"


def test_excluir_subcategoria_com_produto_vinculado(db):
    """Garante conflito ao excluir subcategoria com produtos."""
    _, subcategoria, _, _ = criar_base(db)

    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_subcategoria(db, subcategoria.id)

    assert exc_info.value.status_code == 409


def test_produtos_disponibilidade_criacao_atualizacao_e_erros(db):
    """Cobre disponibilidade, criacao, listagem, update e delete de produtos."""
    _, subcategoria, unidade, _ = criar_base(db)
    produto = repository.criar_produto(
        db,
        ProdutoCreate(
            nome="Restrito",
            descricao=None,
            ativo=True,
            pontos_fidelidade_por_unidade=0,
            disponivel_todas_unidades=False,
            subcategoria_id=subcategoria.id,
            unidade_ids=[unidade.id],
        ),
    )

    assert produto.unidade_ids == [unidade.id]
    assert repository.listar_produtos(db, 0, 10, unidade_id=unidade.id)
    assert repository.obter_produto(db, produto.id) == produto

    atualizado = repository.atualizar_produto(
        db,
        produto.id,
        ProdutoUpdate(nome="Restrito Atualizado", disponivel_todas_unidades=True),
    )
    assert atualizado.nome == "Restrito Atualizado"
    assert atualizado.unidades == []

    repository.excluir_produto(db, produto.id)
    with pytest.raises(HTTPException) as exc_info:
        repository.obter_produto(db, produto.id)
    assert exc_info.value.status_code == 404


def test_produtos_erros_de_validacao_e_integridade(monkeypatch):
    """Cobre erros de produto, disponibilidade e integridade."""
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        repository.criar_produto(
            db,
            ProdutoCreate(nome="X", subcategoria_id=99, disponivel_todas_unidades=True),
        )
    assert exc_info.value.detail == "Subcategoria nao encontrada"

    produto = Produto(id=1, nome="X", disponivel_todas_unidades=False, subcategoria_id=1)
    with pytest.raises(HTTPException) as exc_info:
        repository._aplicar_disponibilidade(db, produto, False, [])
    assert exc_info.value.status_code == 400

    db.query.return_value = FakeQuery(items=[])
    with pytest.raises(HTTPException) as exc_info:
        repository._obter_unidades(db, [1])
    assert exc_info.value.detail == "Unidade nao encontrada"

    db.get.return_value = Subcategoria(id=1, nome="Sub", categoria_id=1)
    db.query.return_value = FakeQuery(items=[Unidade(id=1, nome="U")])
    db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_produto(
            db,
            ProdutoCreate(nome="X", subcategoria_id=1, disponivel_todas_unidades=True),
        )
    assert exc_info.value.detail == "Erro ao criar produto"

    monkeypatch.setattr(repository, "obter_produto", lambda _db, _id: produto)
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_produto(db, 1, ProdutoUpdate(subcategoria_id=2))
    assert exc_info.value.detail == "Subcategoria nao encontrada"

    db.get.return_value = Subcategoria(id=2, nome="Nova", categoria_id=1)
    db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_produto(db, 1, ProdutoUpdate(nome="Y", subcategoria_id=2))
    assert exc_info.value.detail == "Erro ao atualizar produto"

    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_produto(db, 1)
    assert exc_info.value.detail == "Erro ao excluir produto"


def test_listar_produtos_com_query_fake():
    """Garante que listagem aplica filtro, offset e limit."""
    db = Mock()
    query = FakeQuery(items=[Produto(id=1, nome="X")])
    db.query.return_value = query

    assert repository.listar_produtos(db, 5, 20, unidade_id=1) == query.items
    assert query.filtered is True
    assert query.offset_value == 5
    assert query.limit_value == 20


def test_variacoes_fluxo_feliz_e_erros(monkeypatch, db):
    """Cobre CRUD de variacoes e seus erros."""
    _, _, _, produto = criar_base(db)
    variacao = repository.criar_variacao(
        db,
        ProdutoVariacaoCreate(
            produto_id=produto.id,
            nome="Tradicional",
            tipo=TipoVariacao.normal,
            preco=Decimal("19.90"),
        ),
    )

    assert repository.listar_variacoes(db)[0] == variacao
    assert repository.obter_variacao(db, variacao.id) == variacao
    assert repository.atualizar_variacao(
        db,
        variacao.id,
        ProdutoVariacaoUpdate(nome="Duplo"),
    ).nome == "Duplo"
    repository.excluir_variacao(db, variacao.id)

    mock_db = Mock()
    mock_db.query.return_value = FakeQuery(first_item=None)
    with pytest.raises(HTTPException) as exc_info:
        repository.obter_variacao(mock_db, 99)
    assert exc_info.value.detail == "Variacao nao encontrada"

    mock_db.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_variacao(
            mock_db,
            ProdutoVariacaoCreate(
                produto_id=99,
                nome="X",
                tipo=TipoVariacao.normal,
                preco=Decimal("1.00"),
            ),
        )
    assert exc_info.value.detail == "Produto nao encontrado"

    mock_db.get.return_value = Produto(id=1, nome="X", subcategoria_id=1)
    mock_db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_variacao(
            mock_db,
            ProdutoVariacaoCreate(
                produto_id=1,
                nome="X",
                tipo=TipoVariacao.normal,
                preco=Decimal("1.00"),
            ),
        )
    assert exc_info.value.detail == "Erro ao criar variacao"

    monkeypatch.setattr(repository, "obter_variacao", lambda _db, _id: ProdutoVariacao(id=1, nome="X"))
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_variacao(mock_db, 1, ProdutoVariacaoUpdate(nome="Y"))
    assert exc_info.value.detail == "Erro ao atualizar variacao"

    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_variacao(mock_db, 1)
    assert exc_info.value.detail == "Erro ao excluir variacao"


def test_adicionais_fluxo_feliz_e_erros(monkeypatch, db):
    """Cobre CRUD de adicionais e seus erros."""
    _, _, _, produto = criar_base(db)
    adicional = repository.criar_adicional(
        db,
        ProdutoAdicionalCreate(
            produto_id=produto.id,
            nome="Bacon",
            preco=Decimal("4.50"),
        ),
    )

    assert repository.listar_adicionais(db)[0] == adicional
    assert repository.obter_adicional(db, adicional.id) == adicional
    assert repository.atualizar_adicional(
        db,
        adicional.id,
        ProdutoAdicionalUpdate(nome="Bacon Crocante"),
    ).nome == "Bacon Crocante"
    repository.excluir_adicional(db, adicional.id)

    mock_db = Mock()
    mock_db.query.return_value = FakeQuery(first_item=None)
    with pytest.raises(HTTPException) as exc_info:
        repository.obter_adicional(mock_db, 99)
    assert exc_info.value.detail == "Adicional nao encontrado"

    mock_db.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_adicional(
            mock_db,
            ProdutoAdicionalCreate(produto_id=99, nome="X", preco=Decimal("1.00")),
        )
    assert exc_info.value.detail == "Produto nao encontrado"

    mock_db.get.return_value = Produto(id=1, nome="X", subcategoria_id=1)
    mock_db.commit.side_effect = integrity_error()
    with pytest.raises(HTTPException) as exc_info:
        repository.criar_adicional(
            mock_db,
            ProdutoAdicionalCreate(produto_id=1, nome="X", preco=Decimal("1.00")),
        )
    assert exc_info.value.detail == "Erro ao criar adicional"

    monkeypatch.setattr(repository, "obter_adicional", lambda _db, _id: ProdutoAdicional(id=1, nome="X"))
    with pytest.raises(HTTPException) as exc_info:
        repository.atualizar_adicional(mock_db, 1, ProdutoAdicionalUpdate(nome="Y"))
    assert exc_info.value.detail == "Erro ao atualizar adicional"

    with pytest.raises(HTTPException) as exc_info:
        repository.excluir_adicional(mock_db, 1)
    assert exc_info.value.detail == "Erro ao excluir adicional"
