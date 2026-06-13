"""Testes do upload de imagens de unidades."""

import asyncio
from datetime import time

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.unidades import router as unidades_router
from src.unidades.model import Unidade


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.fixture
def db_session():
    """Cria uma sessao SQLite isolada para os testes de upload de unidade."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_criar_unidade_relaciona_imagem(tmp_path, monkeypatch, db_session):
    """Garante criacao da unidade ja relacionada com a imagem enviada."""
    upload_dir = tmp_path / "uploads" / "unidades"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(unidades_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("unidade.png", "image/png", b"fake image content")

    unidade = asyncio.run(
        unidades_router.criar_unidade(
            nome="Unidade Centro",
            abertura=time(9, 0),
            fechamento=time(22, 0),
            cep="58000000",
            logradouro="Rua Principal",
            bairro="Centro",
            cidade="Joao Pessoa",
            estado="PB",
            numero="100",
            complemento=None,
            descricao="Unidade principal",
            imagem=arquivo,
            db=db_session,
        )
    )

    unidade_salva = db_session.get(Unidade, unidade.id)
    assert unidade_salva is not None
    assert unidade_salva.imagem == unidade.imagem
    assert unidade.imagem.startswith("/uploads/unidades/")
    assert unidade.imagem.endswith(".png")
    assert len(list(upload_dir.iterdir())) == 1


def test_criar_unidade_rejeita_arquivo_nao_imagem(tmp_path, monkeypatch, db_session):
    """Garante que unidade aceita apenas arquivos de imagem."""
    upload_dir = tmp_path / "uploads" / "unidades"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(unidades_router, "UPLOAD_DIR", upload_dir)
    arquivo = FakeUploadFile("unidade.txt", "text/plain", b"not an image")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            unidades_router.criar_unidade(
                nome="Unidade Centro",
                abertura=time(9, 0),
                fechamento=time(22, 0),
                cep="58000000",
                logradouro="Rua Principal",
                bairro="Centro",
                cidade="Joao Pessoa",
                estado="PB",
                numero=None,
                complemento=None,
                descricao=None,
                imagem=arquivo,
                db=db_session,
            )
        )

    assert exc_info.value.status_code == 400
    assert db_session.query(Unidade).count() == 0
    assert list(upload_dir.iterdir()) == []
