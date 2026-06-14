from datetime import datetime, time
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src.pedidos.model import ItemPedido, Pedido, StatusItemPedido, StatusPedido
from src.produtos.model import Categoria, Produto, ProdutoVariacao, Subcategoria, TipoVariacao
from src.unidades.model import Endereco, Unidade

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(name="db_session", scope="function")
def fixture_db_session():
    """Cria uma sessao SQLite isolada para os testes de BI."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """Substitui a dependencia de banco pela sessao de teste."""

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
    """Cria o TestClient usado nos cenarios de BI."""
    return TestClient(app)


@pytest.fixture(name="pedido_pago")
def fixture_pedido_pago(db_session):
    """Cria um pedido pago com item vendido para alimentar o dashboard."""
    endereco = Endereco(
        cep="71900000",
        logradouro="Aguas Claras",
        numero="1",
        bairro="Aguas Claras",
        cidade="Brasilia",
        estado="DF",
    )
    unidade = Unidade(
        nome="Unidade BI",
        abertura=time(16, 30),
        fechamento=time(23, 59),
        descricao="Unidade teste",
        endereco=endereco,
    )
    categoria = Categoria(nome="Hot-Dog")
    subcategoria = Subcategoria(nome="Lanches", categoria=categoria)
    produto = Produto(
        nome="Paraiba Monster XL",
        descricao="Produto destaque",
        ativo=True,
        pontos_fidelidade_por_unidade=1,
        disponivel_todas_unidades=True,
        subcategoria=subcategoria,
    )
    variacao = ProdutoVariacao(
        produto=produto,
        nome="Normal",
        tipo=TipoVariacao.normal,
        preco=Decimal("30.00"),
        ativo=True,
    )
    pedido = Pedido(
        unidade=unidade,
        nome_comanda="Mesa 1",
        status=StatusPedido.pago,
        subtotal=Decimal("60.00"),
        desconto_fidelidade=Decimal("0.00"),
        total=Decimal("60.00"),
        created_at=datetime.now().replace(hour=13, minute=0, second=0, microsecond=0),
        fechado_em=datetime.now(),
    )
    pedido.itens = [
        ItemPedido(
            produto_variacao=variacao,
            produto_id=1,
            produto_nome="Paraiba Monster XL",
            produto_variacao_nome="Normal",
            quantidade=2,
            preco_unitario=Decimal("30.00"),
            status=StatusItemPedido.entregue,
            lote=1,
            created_at=pedido.created_at,
        )
    ]
    db_session.add(pedido)
    db_session.commit()
    return pedido


@pytest.mark.integration
@pytest.mark.usefixtures("pedido_pago")
def test_dashboard_retorna_indicadores_agregados(cliente):
    """Garante que o BI consolida pedidos e itens vendidos."""
    resposta = cliente.get("/bi/dashboard")

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["kpis"]["receita_bruta"] == "60.00"
    assert body["kpis"]["lucro_liquido"] == "60.00"
    assert body["kpis"]["ticket_medio"] == "60.00"
    assert body["kpis"]["total_pedidos"] == 1
    assert body["top_produtos"][0]["nome"] == "Paraiba Monster XL"
    assert body["top_produtos"][0]["quantidade"] == 2
    assert body["mix_produtos"][0]["percentual"] == "100.00"
    assert body["destaque"]["nome"] == "Paraiba Monster XL"
