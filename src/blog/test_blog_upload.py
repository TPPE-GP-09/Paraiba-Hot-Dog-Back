"""Testes do upload de imagens do blog."""

import asyncio
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.blog.model import Blog, TipoNoticiaPromocao
from src.blog import router as blog_router
from src.blog.schema import BlogCreate
from src.database import Base


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria uma sessao SQLite isolada para os testes de upload do blog."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[Blog.__table__])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine, tables=[Blog.__table__])


def test_criar_post_relaciona_imagem_ao_blog(tmp_path, monkeypatch, db_session):
    """Garante criacao do post ja relacionado com a imagem enviada."""
    upload_dir = tmp_path / "uploads" / "blog"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(blog_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("post.jpg", "image/jpeg", b"fake image content")

    imagem_url = asyncio.run(blog_router.salvar_imagem_upload(arquivo))
    post = blog_router.repository.criar_post(
        db_session,
        BlogCreate(
            titulo="Promocao nova",
            tipo=TipoNoticiaPromocao.promocao,
            data=date(2026, 6, 12),
            descricao="Descricao da promocao",
            imagem_url=imagem_url,
        ),
    )

    post_salvo = db_session.get(Blog, post.id)
    assert post_salvo is not None
    assert post_salvo.imagem_url == post.imagem_url
    assert post.imagem_url.startswith("/uploads/blog/")
    assert post.imagem_url.endswith(".jpg")
    assert len(list(upload_dir.iterdir())) == 1


def test_criar_post_rejeita_arquivo_nao_imagem(tmp_path, monkeypatch, db_session):
    """Garante que o endpoint aceita apenas arquivos de imagem."""
    upload_dir = tmp_path / "uploads" / "blog"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(blog_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("post.txt", "text/plain", b"not an image")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(blog_router.salvar_imagem_upload(arquivo))

    assert exc_info.value.status_code == 400
    assert db_session.query(Blog).count() == 0
    assert not list(upload_dir.iterdir())
