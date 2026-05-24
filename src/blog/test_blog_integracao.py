"""Testes de integracao local dos endpoints de blog com TestClient."""

# Pylint doesn't understand pytest fixtures in this module.
# pylint: disable=redefined-outer-name,unused-argument

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.blog.model import Blog, TipoNoticiaPromocao
from src.database import Base, get_db
from src.main import app
from src.security import get_current_user

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
def authenticated_user():
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "roles": ["administrador"],
    }
    yield
    app.dependency_overrides.pop(get_current_user, None)


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


def test_listar_vazio(override_get_db):
    response = client.get("/blog/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_com_dados(override_get_db, post_valido):
    response = client.get("/blog/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["titulo"] == "Nova Unidade Abre"


def test_filtrar_por_tipo(override_get_db, db_session):
    p1 = Blog(titulo="Notícia 1", tipo=TipoNoticiaPromocao.noticia, data=date(2026, 4, 1))
    p2 = Blog(titulo="Promo 1", tipo=TipoNoticiaPromocao.promocao, data=date(2026, 4, 2))
    db_session.add_all([p1, p2])
    db_session.commit()

    response = client.get("/blog/?tipo=noticia")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["tipo"] == "noticia"


def test_obter_por_id(override_get_db, post_valido):
    response = client.get(f"/blog/{post_valido.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_valido.id
    assert data["titulo"] == "Nova Unidade Abre"


def test_atualizar_post(override_get_db, authenticated_user, post_valido):
    payload = {"titulo": "Novo Título"}
    response = client.patch(f"/blog/{post_valido.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Novo Título"


def test_excluir_post(override_get_db, authenticated_user, post_valido):
    response = client.delete(f"/blog/{post_valido.id}")
    assert response.status_code == 204

    response = client.get(f"/blog/{post_valido.id}")
    assert response.status_code == 404
