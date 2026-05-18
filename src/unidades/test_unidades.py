"""Tests for unidades endpoints."""

# Pylint doesn't understand pytest fixtures in this module.
# pylint: disable=redefined-outer-name,unused-argument

from datetime import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.unidades.model import Endereco, Unidade

client = TestClient(app)

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria uma nova sessão de banco de dados para cada teste"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def override_get_db(db_session):
    """Substitui a dependência get_db pela sessão de teste"""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def endereco_valido(db_session):
    """Cria um endereço válido para os testes"""
    endereco = Endereco(
        cep="58000000",
        logradouro="Rua Test",
        numero="123",
        complemento="Apto 1",
        bairro="Centro",
        cidade="João Pessoa",
        estado="PB"
    )
    db_session.add(endereco)
    db_session.commit()
    db_session.refresh(endereco)
    return endereco


@pytest.fixture
def unidade_valida(db_session, endereco_valido):
    """Cria uma unidade válida para os testes"""
    unidade = Unidade(
        nome="Unidade Centro",
        imagem="https://example.com/unidade.jpg",
        abertura=time(10, 0),
        fechamento=time(22, 0),
        descricao="Unidade principal",
        endereco_id=endereco_valido.id
    )
    db_session.add(unidade)
    db_session.commit()
    db_session.refresh(unidade)
    return unidade


class TestUnidades:
    """Testes para os endpoints de unidades"""

    def test_listar_unidades_vazio(self, override_get_db):
        """Testa listagem de unidades quando não há nenhuma"""
        response = client.get("/unidades/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_unidades_com_dados(self, override_get_db, unidade_valida):
        """Testa listagem de unidades com dados"""
        response = client.get("/unidades/")
        assert response.status_code == 200
        unidades = response.json()
        assert len(unidades) == 1
        assert unidades[0]["nome"] == "Unidade Centro"
        assert unidades[0]["abertura"] == "10:00:00"
        assert unidades[0]["fechamento"] == "22:00:00"

    def test_obter_unidade_por_id(self, override_get_db, unidade_valida):
        """Testa obtenção de uma unidade por ID"""
        response = client.get(f"/unidades/{unidade_valida.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == unidade_valida.id
        assert data["nome"] == "Unidade Centro"
        assert data["descricao"] == "Unidade principal"

    def test_obter_unidade_inexistente(self, override_get_db):
        """Testa obtenção de uma unidade que não existe"""
        response = client.get("/unidades/9999")
        assert response.status_code == 404
        assert "Unidade nao encontrada" in response.json()["detail"]

    def test_criar_unidade(self, override_get_db, db_session):
        """Testa criação de uma nova unidade"""
        payload = {
            "nome": "Unidade Campina Grande",
            "imagem": "https://example.com/campina.jpg",
            "abertura": "11:00:00",
            "fechamento": "23:00:00",
            "descricao": "Unidade em Campina Grande",
            "endereco": {
                "cep": "58100000",
                "logradouro": "Av. Brasília",
                "numero": "456",
                "complemento": "Loja 2",
                "bairro": "Prata",
                "cidade": "Campina Grande",
                "estado": "PB"
            }
        }
        response = client.post("/unidades/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Unidade Campina Grande"
        assert data["abertura"] == "11:00:00"
        assert data["endereco"]["cidade"] == "Campina Grande"

    def test_criar_unidade_com_endereco_incompleto(self, override_get_db):
        """Testa criação de unidade com endereço inválido"""
        payload = {
            "nome": "Unidade Teste",
            "abertura": "10:00:00",
            "fechamento": "22:00:00",
            "endereco": {
                "cep": "58000000",
                "logradouro": "Rua Teste"
            }
        }
        response = client.post("/unidades/", json=payload)
        assert response.status_code == 422

    def test_criar_unidade_sem_endereco(self, override_get_db):
        """Testa criação de unidade sem endereço"""
        payload = {
            "nome": "Unidade Teste",
            "abertura": "10:00:00",
            "fechamento": "22:00:00"
        }
        response = client.post("/unidades/", json=payload)
        assert response.status_code == 422

    def test_excluir_unidade(self, override_get_db, unidade_valida):
        """Testa exclusão de uma unidade"""
        unidade_id = unidade_valida.id
        response = client.delete(f"/unidades/{unidade_id}")
        assert response.status_code == 204

        response = client.get(f"/unidades/{unidade_id}")
        assert response.status_code == 404

    def test_excluir_unidade_inexistente(self, override_get_db):
        """Testa exclusão de uma unidade que não existe"""
        response = client.delete("/unidades/9999")
        assert response.status_code == 404

    def test_validacao_horario_abertura(self, override_get_db):
        """Testa validação de horário de abertura"""
        payload = {
            "nome": "Unidade Teste",
            "imagem": "https://example.com/teste.jpg",
            "abertura": "25:00:00",
            "fechamento": "22:00:00",
            "descricao": "Teste",
            "endereco": {
                "cep": "58000000",
                "logradouro": "Rua Teste",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "João Pessoa",
                "estado": "PB"
            }
        }
        response = client.post("/unidades/", json=payload)
        assert response.status_code == 422

    def test_endereco_da_unidade_relacionado(self, override_get_db, unidade_valida):
        """Testa se o endereço está corretamente relacionado à unidade"""
        response = client.get(f"/unidades/{unidade_valida.id}")
        assert response.status_code == 200
        data = response.json()

        endereco = data["endereco"]
        assert endereco["cep"] == "58000000"
        assert endereco["logradouro"] == "Rua Test"
        assert endereco["numero"] == "123"
        assert endereco["bairro"] == "Centro"
        assert endereco["cidade"] == "João Pessoa"
        assert endereco["estado"] == "PB"
