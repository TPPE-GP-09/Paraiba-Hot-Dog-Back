"""Testes do upload de imagens de produtos."""

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.produtos import router as produtos_router
from src.produtos.model import Categoria, Produto, Subcategoria


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.fixture
def db_session():
    """Cria uma sessao SQLite isolada para os testes de upload de produto."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        categoria = Categoria(nome="Hot Dogs")
        db.add(categoria)
        db.flush()
        subcategoria = Subcategoria(nome="Tradicionais", categoria_id=categoria.id)
        db.add(subcategoria)
        db.commit()
        yield db, subcategoria
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_criar_produto_relaciona_imagem(tmp_path, monkeypatch, db_session):
    """Garante criacao do produto ja relacionado com a imagem enviada."""
    db, subcategoria = db_session
    upload_dir = tmp_path / "uploads" / "produtos"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(produtos_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("produto.jpg", "image/jpeg", b"fake image content")

    produto = asyncio.run(
        produtos_router.criar_produto(
            nome="Hot dog simples",
            subcategoria_id=subcategoria.id,
            descricao="Classico",
            ativo=True,
            pontos_fidelidade_por_unidade=0,
            disponivel_todas_unidades=True,
            unidade_ids=None,
            file=arquivo,
            db=db,
        )
    )

    produto_salvo = db.get(Produto, produto.id)
    assert produto_salvo is not None
    assert produto_salvo.imagem_url == produto.imagem_url
    assert produto.imagem_url.startswith("/uploads/produtos/")
    assert produto.imagem_url.endswith(".jpg")
    assert len(list(upload_dir.iterdir())) == 1


def test_criar_produto_rejeita_arquivo_nao_imagem(tmp_path, monkeypatch, db_session):
    """Garante que produto aceita apenas arquivos de imagem."""
    db, subcategoria = db_session
    upload_dir = tmp_path / "uploads" / "produtos"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(produtos_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("produto.txt", "text/plain", b"not an image")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            produtos_router.criar_produto(
                nome="Hot dog simples",
                subcategoria_id=subcategoria.id,
                descricao=None,
                ativo=True,
                pontos_fidelidade_por_unidade=0,
                disponivel_todas_unidades=True,
                unidade_ids=None,
                file=arquivo,
                db=db,
            )
        )

    assert exc_info.value.status_code == 400
    assert db.query(Produto).count() == 0
    assert list(upload_dir.iterdir()) == []
