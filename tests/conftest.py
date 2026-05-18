import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db

# Conexão com o banco de dados PostgreSQL de teste (pode ser sobrescrita via variável de ambiente)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@postgres:5432/paraiba_hotdog_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def configurar_banco_teste():
    # Cria as tabelas necessárias para os testes no banco
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture()
def sessao_banco():
    conexao = engine.connect()
    transacao = conexao.begin()
    sessao = TestingSessionLocal(bind=conexao)
    
    yield sessao
    
    sessao.close()
    transacao.rollback()
    conexao.close()

@pytest.fixture()
def cliente(sessao_banco):
    def override_get_db():
        yield sessao_banco

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as cliente_teste:
        yield cliente_teste
    app.dependency_overrides.clear()
