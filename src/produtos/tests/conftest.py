import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app

# Configuração do banco SQLite em memória para isolar os testes
TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """Cria uma nova sessão de banco de dados SQLite em memória para cada teste."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """Substitui automaticamente a dependência get_db do FastAPI pela sessão de teste."""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(name="cliente")
def fixture_cliente():
    """Entrega o cliente de testes do FastAPI pronto."""
    return TestClient(app)

@pytest.fixture
def dados_base(cliente):
    resposta_categoria = cliente.post("/produtos/categorias", json={"nome": "Hot-Dog"})
    assert resposta_categoria.status_code == 201
    categoria = resposta_categoria.json()

    resposta_subcategoria = cliente.post("/produtos/subcategorias", json={
        "nome": "Molho",
        "categoria_id": categoria["id"]
    })
    assert resposta_subcategoria.status_code == 201
    subcategoria = resposta_subcategoria.json()

    resposta_produto = cliente.post("/produtos/", json={
        "nome": "Tradicional",
        "descricao": "Pao de leite Ninho, salsicha Perdigao, queijo mucarela, molho de tomate, milho e batata palha.",
        "imagem_url": None,
        "ativo": True,
        "pontos_fidelidade_por_unidade": 1,
        "disponivel_todas_unidades": True,
        "subcategoria_id": subcategoria["id"]
    })
    assert resposta_produto.status_code == 201
    produto = resposta_produto.json()

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "produto": produto
    }
