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
from src.unidades.schema import EnderecoCreate, UnidadeCreate


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


class FakeForm(dict):
    def getlist(self, key: str) -> list:
        value = self.get(key)
        return value if isinstance(value, list) else []


class FakeMultipartRequest:
    headers = {"content-type": "multipart/form-data"}

    def __init__(self, form_data: dict):
        self._form_data = FakeForm(form_data)

    async def form(self):
        return self._form_data


@pytest.fixture(name="db_session")
def fixture_db_session():
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

    imagem_url = asyncio.run(unidades_router.salvar_imagem_upload(arquivo))
    unidade = unidades_router.repository.criar_unidade(
        db_session,
        UnidadeCreate(
            nome="Unidade Centro",
            abertura=time(9, 0),
            fechamento=time(22, 0),
            descricao="Unidade principal",
            imagem=imagem_url,
            endereco=EnderecoCreate(
                cep="58000000",
                logradouro="Rua Principal",
                bairro="Centro",
                cidade="Joao Pessoa",
                estado="PB",
                numero="100",
                complemento=None,
            ),
        ),
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
        asyncio.run(unidades_router.salvar_imagem_upload(arquivo))

    assert exc_info.value.status_code == 400
    assert db_session.query(Unidade).count() == 0
    assert not list(upload_dir.iterdir())


def test_unidade_multipart_valida_limite_estado(tmp_path, monkeypatch):
    """Garante 422 antes do banco quando estado excede o limite da coluna."""
    upload_dir = tmp_path / "uploads" / "unidades"
    upload_dir.mkdir(parents=True)
    monkeypatch.setattr(unidades_router, "UPLOAD_DIR", upload_dir)
    request = FakeMultipartRequest(
        {
            "nome": "Unidade Centro",
            "abertura": "11:00:00",
            "fechamento": "23:00:00",
            "cep": "58000000",
            "logradouro": "Rua Principal",
            "numero": "100",
            "complemento": None,
            "bairro": "Centro",
            "cidade": "Joao Pessoa",
            "estado": "aoba",
            "descricao": "Unidade principal",
            "imagem": FakeUploadFile("unidade.png", "image/png", b"fake image content"),
        }
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(unidades_router._unidade_data_from_request(request))

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail[0]["loc"] == ("endereco", "estado")
