import os
from datetime import UTC, datetime

import httpx
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def _unique_email(prefix: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}.{stamp}@example.com"


def _create_unidade() -> int:
    payload = {
        "nome": f"Unidade Teste {datetime.now(UTC).strftime('%H%M%S%f')}",
        "imagem": None,
        "abertura": "11:00:00",
        "fechamento": "23:00:00",
        "descricao": "Unidade para teste de integracao",
        "endereco": {
            "cep": "58000000",
            "logradouro": "Rua de Teste",
            "numero": "123",
            "complemento": None,
            "bairro": "Centro",
            "cidade": "Joao Pessoa",
            "estado": "PB",
        },
    }
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(f"{BASE_URL}/unidades/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.mark.parametrize(
    "nome,funcao",
    [
        ("Usuario Caixa", "caixa"),
        ("Usuario Cozinha", "cozinha"),
        ("Usuario Admin", "administrador"),
    ],
)
def test_criar_usuario_com_unidade_valida(nome: str, funcao: str) -> None:
    unidade_id = _create_unidade()
    payload = {
        "nome": nome,
        "email": _unique_email("usuario.valido"),
        "senha": "12345678",
        "funcao": funcao,
        "unidade_id": unidade_id,
        "permissao_ids": [],
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(f"{BASE_URL}/usuarios/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == payload["email"]
    assert body["nome"] == payload["nome"]
    assert body["funcao"] == payload["funcao"]
    assert body["unidade_id"] == unidade_id


@pytest.mark.parametrize("unidade_id_invalida", [999999, 123456789])
def test_criar_usuario_com_unidade_inexistente_retorna_404(unidade_id_invalida: int) -> None:
    payload = {
        "nome": "Usuario Unidade Invalida",
        "email": _unique_email("usuario.invalido"),
        "senha": "12345678",
        "funcao": "caixa",
        "unidade_id": unidade_id_invalida,
        "permissao_ids": [],
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(f"{BASE_URL}/usuarios/", json=payload)

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Unidade nao encontrada"


def test_atualizar_usuario_com_unidade_inexistente_retorna_404() -> None:
    unidade_id = _create_unidade()
    create_payload = {
        "nome": "Usuario Atualizacao",
        "email": _unique_email("usuario.update"),
        "senha": "12345678",
        "funcao": "caixa",
        "unidade_id": unidade_id,
        "permissao_ids": [],
    }

    with httpx.Client(timeout=10.0) as client:
        create_resp = client.post(f"{BASE_URL}/usuarios/", json=create_payload)
        assert create_resp.status_code == 201, create_resp.text
        usuario_id = create_resp.json()["id"]

        patch_resp = client.patch(
            f"{BASE_URL}/usuarios/{usuario_id}",
            json={"unidade_id": 999999},
        )

    assert patch_resp.status_code == 404, patch_resp.text
    assert patch_resp.json()["detail"] == "Unidade nao encontrada"


def test_listar_usuarios_retorna_200() -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/usuarios/")

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_obter_usuario_existente_retorna_200() -> None:
    unidade_id = _create_unidade()
    payload = {
        "nome": "Usuario Get",
        "email": _unique_email("usuario.get"),
        "senha": "12345678",
        "funcao": "caixa",
        "unidade_id": unidade_id,
        "permissao_ids": [],
    }

    with httpx.Client(timeout=10.0) as client:
        create_resp = client.post(f"{BASE_URL}/usuarios/", json=payload)
        assert create_resp.status_code == 201, create_resp.text
        usuario_id = create_resp.json()["id"]

        get_resp = client.get(f"{BASE_URL}/usuarios/{usuario_id}")

    assert get_resp.status_code == 200, get_resp.text
    body = get_resp.json()
    assert body["id"] == usuario_id
    assert body["email"] == payload["email"]


def test_obter_usuario_inexistente_retorna_404() -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/usuarios/999999999")

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Usuario nao encontrado"


def test_deletar_usuario_remove_e_get_retorna_404() -> None:
    unidade_id = _create_unidade()
    payload = {
        "nome": "Usuario Delete",
        "email": _unique_email("usuario.delete"),
        "senha": "12345678",
        "funcao": "caixa",
        "unidade_id": unidade_id,
        "permissao_ids": [],
    }

    with httpx.Client(timeout=10.0) as client:
        create_resp = client.post(f"{BASE_URL}/usuarios/", json=payload)
        assert create_resp.status_code == 201, create_resp.text
        usuario_id = create_resp.json()["id"]

        delete_resp = client.delete(f"{BASE_URL}/usuarios/{usuario_id}")
        assert delete_resp.status_code == 204, delete_resp.text

        get_resp = client.get(f"{BASE_URL}/usuarios/{usuario_id}")

    assert get_resp.status_code == 404, get_resp.text
    assert get_resp.json()["detail"] == "Usuario nao encontrado"
