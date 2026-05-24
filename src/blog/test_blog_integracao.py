"""Testes de integracao para os endpoints de blog."""

# pylint: disable=redefined-outer-name

import os
from datetime import UTC, datetime

import httpx
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

pytestmark = pytest.mark.integration


def _payload_post(**overrides):
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    payload = {
        "titulo": f"Post Integracao {stamp}",
        "imagem_url": "https://example.com/post.jpg",
        "descricao": "Post para teste de integracao",
        "tipo": "noticia",
        "data": "2026-05-22",
    }
    payload.update(overrides)
    return payload


@pytest.fixture(name="api_client")
def fixture_api_client() -> httpx.Client:
    with httpx.Client(timeout=10.0) as client:
        try:
            health = client.get(f"{BASE_URL}/")
            health.raise_for_status()
        except httpx.HTTPError as exc:
            pytest.skip(f"API de integracao indisponivel em {BASE_URL}: {exc}")
        yield client


@pytest.fixture(name="cleanup_ids")
def fixture_cleanup_ids():
    """Fixture para limpeza de posts criados durante o teste."""
    ids = []
    yield ids


def test_listar_posts_vazio(api_client: httpx.Client):
    """Testa listagem de posts vazio."""
    response = api_client.get(f"{BASE_URL}/blog/")
    assert response.status_code == 200


def test_criar_post(api_client: httpx.Client, cleanup_ids):
    """Testa criacao de um novo post."""
    payload = _payload_post(titulo="Post de Teste")
    response = api_client.post(f"{BASE_URL}/blog/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Post de Teste"
    assert data["tipo"] == "noticia"
    cleanup_ids.append(data["id"])


def test_criar_post_promocao(api_client: httpx.Client, cleanup_ids):
    """Testa criacao de um post de promocao."""
    payload = _payload_post(titulo="Promoção", tipo="promocao")
    response = api_client.post(f"{BASE_URL}/blog/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "promocao"
    cleanup_ids.append(data["id"])


def test_obter_post(api_client: httpx.Client, cleanup_ids):
    """Testa obtencao de um post especifico."""
    # Cria um post
    payload = _payload_post(titulo="Post para Obter")
    response = api_client.post(f"{BASE_URL}/blog/", json=payload)
    post_id = response.json()["id"]
    cleanup_ids.append(post_id)

    # Obtém o post
    response = api_client.get(f"{BASE_URL}/blog/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["titulo"] == "Post para Obter"


def test_atualizar_post(api_client: httpx.Client, cleanup_ids):
    """Testa atualizacao de um post."""
    # Cria um post
    payload = _payload_post(titulo="Post Original")
    response = api_client.post(f"{BASE_URL}/blog/", json=payload)
    post_id = response.json()["id"]
    cleanup_ids.append(post_id)

    # Atualiza o post
    update_payload = {"titulo": "Post Atualizado"}
    response = api_client.patch(f"{BASE_URL}/blog/{post_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Post Atualizado"


def test_deletar_post(api_client: httpx.Client, cleanup_ids):
    """Testa delecao de um post."""
    # Cria um post
    payload = _payload_post(titulo="Post para Deletar")
    response = api_client.post(f"{BASE_URL}/blog/", json=payload)
    post_id = response.json()["id"]

    # Deleta o post
    response = api_client.delete(f"{BASE_URL}/blog/{post_id}")
    assert response.status_code == 204

    # Verifica se foi deletado
    response = api_client.get(f"{BASE_URL}/blog/{post_id}")
    assert response.status_code == 404


def test_filtrar_posts_por_tipo(api_client: httpx.Client, cleanup_ids):
    """Testa filtragem de posts por tipo."""
    # Cria um post de noticia
    payload1 = _payload_post(titulo="Noticia", tipo="noticia")
    response1 = api_client.post(f"{BASE_URL}/blog/", json=payload1)
    cleanup_ids.append(response1.json()["id"])

    # Cria um post de promocao
    payload2 = _payload_post(titulo="Promocao", tipo="promocao")
    response2 = api_client.post(f"{BASE_URL}/blog/", json=payload2)
    cleanup_ids.append(response2.json()["id"])

    # Filtra por tipo
    response = api_client.get(f"{BASE_URL}/blog/?tip=noticia")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["tipo"] == "noticia"
