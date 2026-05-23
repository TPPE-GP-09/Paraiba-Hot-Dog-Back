from datetime import time
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# pylint: disable=redefined-outer-name

from src.clientes.model import Cliente
from src.database import Base, get_db
from src.main import app
from src.produtos.model import Categoria, Produto, ProdutoAdicional, ProdutoVariacao, Subcategoria, TipoVariacao
from src.unidades.model import Endereco, Unidade


TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(name="cliente")
def fixture_cliente():
    return TestClient(app)


@pytest.fixture
def cardapio_base(db_session):
    endereco = Endereco(
        cep="71900000",
        logradouro="Aguas Claras",
        numero="1",
        bairro="Aguas Claras",
        cidade="Brasilia",
        estado="DF",
    )
    db_session.add(endereco)
    db_session.flush()

    unidade = Unidade(
        nome="Paraiba Hot Dog Sul Aguas Claras",
        abertura=time(16, 30),
        fechamento=time(23, 59),
        descricao="Unidade teste",
        endereco_id=endereco.id,
    )
    categoria = Categoria(nome="Hot-Dog")
    db_session.add_all([unidade, categoria])
    db_session.flush()

    subcategoria = Subcategoria(nome="Molho", categoria_id=categoria.id)
    db_session.add(subcategoria)
    db_session.flush()

    produto = Produto(
        nome="Tradicional",
        descricao="Pao, salsicha, queijo, molho, milho e batata palha.",
        ativo=True,
        pontos_fidelidade_por_unidade=1,
        disponivel_todas_unidades=True,
        subcategoria_id=subcategoria.id,
    )
    db_session.add(produto)
    db_session.flush()

    variacao = ProdutoVariacao(
        produto_id=produto.id,
        nome="Tradicional",
        tipo=TipoVariacao.normal,
        preco=Decimal("19.90"),
        ativo=True,
    )
    adicional_ervas = ProdutoAdicional(
        produto_id=produto.id,
        nome="Maionese Artesanal de Ervas",
        preco=Decimal("3.00"),
    )
    adicional_bacon = ProdutoAdicional(
        produto_id=produto.id,
        nome="Maionese Artesanal de Bacon",
        preco=Decimal("3.00"),
    )
    cliente = Cliente(
        nome="Cliente Teste",
        telefone="61999990001",
        email="cliente.teste@paraibahotdog.com",
        pontos_fidelidade=0,
        ativo=True,
    )
    db_session.add_all([variacao, adicional_ervas, adicional_bacon, cliente])
    db_session.commit()

    return {
        "unidade": unidade,
        "produto": produto,
        "variacao": variacao,
        "adicionais": [adicional_ervas, adicional_bacon],
        "cliente": cliente,
    }
