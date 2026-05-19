"""Tests for blog endpoints."""

# Pylint doesn't understand pytest fixtures in this module.
# pylint: disable=redefined-outer-name,unused-argument

from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.blog.model import Blog, TipoNoticiaPromocao

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
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def post_valido(db_session):
    post = Blog(
        titulo="Nova Unidade Abre",
        imagem_url="https://example.com/post.jpg",
        descricao="Abrimos uma nova unidade no Lago Sul",
        tipo=TipoNoticiaPromocao.noticia,
        data=date(2026, 4, 10),
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


class TestBlog:
    def test_listar_vazio(self, override_get_db):
        response = client.get("/blog/")
        assert response.status_code == 200
        assert response.json() == []

    def test_criar_post(self, override_get_db):
        payload = {
            "titulo": "Promoção de Verão",
            "imagem_url": "https://example.com/promo.jpg",
            "descricao": "Aproveite nossa promoção",
            "tipo": "promocao",
            "data": "2026-05-01",
        }
        response = client.post("/blog/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Promoção de Verão"
        assert data["tipo"] == "promocao"

    def test_listar_com_dados(self, override_get_db, post_valido):
        response = client.get("/blog/")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["titulo"] == "Nova Unidade Abre"

    def test_filtrar_por_tipo(self, override_get_db, db_session):
        # cria dois posts de tipos diferentes
        p1 = Blog(titulo="Notícia 1", tipo=TipoNoticiaPromocao.noticia, data=date(2026, 4, 1))
        p2 = Blog(titulo="Promo 1", tipo=TipoNoticiaPromocao.promocao, data=date(2026, 4, 2))
        db_session.add_all([p1, p2])
        db_session.commit()

        response = client.get("/blog/?tip=noticia")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["tipo"] == "noticia"

    def test_obter_por_id(self, override_get_db, post_valido):
        response = client.get(f"/blog/{post_valido.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post_valido.id
        assert data["titulo"] == "Nova Unidade Abre"

    def test_atualizar_post(self, override_get_db, post_valido):
        payload = {"titulo": "Novo Título"}
        response = client.patch(f"/blog/{post_valido.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Novo Título"

    def test_excluir_post(self, override_get_db, post_valido):
        response = client.delete(f"/blog/{post_valido.id}")
        assert response.status_code == 204

        response = client.get(f"/blog/{post_valido.id}")
        assert response.status_code == 404

    def test_criar_invalido(self, override_get_db):
        # sem titulo
        payload = {"imagem_url": "https://example.com/x.jpg", "tipo": "noticia", "data": "2026-05-01"}
        response = client.post("/blog/", json=payload)
        assert response.status_code == 422
