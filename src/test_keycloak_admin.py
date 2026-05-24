import json
from urllib.error import HTTPError, URLError

import pytest
from fastapi import HTTPException

from src import keycloak_admin


class FakeResponse:
    def __init__(self, body: str = "", status: int = 200, headers: dict[str, str] | None = None):
        self.body = body
        self.status = status
        self.headers = headers or {"content-type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self.body.encode("utf-8")

    def close(self) -> None:
        return None


def http_error(status_code: int, body: str = "{}") -> HTTPError:
    return HTTPError("http://keycloak", status_code, "erro", {}, FakeResponse(body))


def test_request_monta_json_form_headers_e_parseia_resposta(monkeypatch):
    capturado = {}

    def fake_urlopen(request, timeout):
        capturado["method"] = request.get_method()
        capturado["headers"] = dict(request.header_items())
        capturado["body"] = request.data.decode("utf-8")
        capturado["timeout"] = timeout
        return FakeResponse(json.dumps({"ok": True}))

    monkeypatch.setattr(keycloak_admin, "urlopen", fake_urlopen)

    status, body, headers = keycloak_admin._request(
        "POST",
        "http://keycloak/users",
        token="admin-token",
        data={"nome": "Teste"},
    )

    assert status == 200
    assert body == {"ok": True}
    assert headers["content-type"] == "application/json"
    assert capturado["method"] == "POST"
    assert capturado["headers"]["Authorization"] == "Bearer admin-token"
    assert capturado["headers"]["Content-type"] == "application/json"
    assert capturado["body"] == '{"nome": "Teste"}'
    assert capturado["timeout"] == 10


def test_request_parseia_formulario(monkeypatch):
    capturado = {}

    def fake_urlopen(request, timeout):
        assert timeout == 10
        capturado["body"] = request.data.decode("utf-8")
        capturado["headers"] = dict(request.header_items())
        return FakeResponse()

    monkeypatch.setattr(keycloak_admin, "urlopen", fake_urlopen)

    status, body, _ = keycloak_admin._request(
        "POST",
        "http://keycloak/token",
        form={"grant_type": "password", "username": "admin"},
    )

    assert status == 200
    assert body is None
    assert "grant_type=password" in capturado["body"]
    assert capturado["headers"]["Content-type"] == "application/x-www-form-urlencoded"


def test_request_retorna_http_error_esperado(monkeypatch):
    monkeypatch.setattr(
        keycloak_admin,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(http_error(404, '{"erro": true}')),
    )

    status, body, _ = keycloak_admin._request(
        "GET",
        "http://keycloak/users",
        expected_statuses=(404,),
    )

    assert status == 404
    assert body == {"erro": True}


def test_request_converte_http_error_inesperado(monkeypatch):
    monkeypatch.setattr(
        keycloak_admin,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(http_error(403)),
    )

    with pytest.raises(HTTPException) as exc_info:
        keycloak_admin._request("GET", "http://keycloak/users")

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == "Credenciais administrativas do Keycloak invalidas"


def test_request_converte_falha_de_conexao(monkeypatch):
    monkeypatch.setattr(
        keycloak_admin,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("fora")),
    )

    with pytest.raises(HTTPException) as exc_info:
        keycloak_admin._request("GET", "http://keycloak/users")

    assert exc_info.value.status_code == 502


def test_keycloak_exception_mapeia_conflito_e_erro_generico():
    assert keycloak_admin._keycloak_exception(409).status_code == 409
    erro = keycloak_admin._keycloak_exception(500)
    assert erro.status_code == 502
    assert erro.detail == "Falha ao consultar o Keycloak: HTTP 500"


def test_admin_token_e_urls(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_admin_base_url", "http://keycloak:8080/")
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_realm", "paraiba-hotdog")
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda *_args, **_kwargs: (200, {"access_token": "admin-token"}, {}),
    )

    assert keycloak_admin._realm_admin_url("/users") == (
        "http://keycloak:8080/admin/realms/paraiba-hotdog/users"
    )
    assert keycloak_admin._admin_token() == "admin-token"


def test_busca_primeiro_id_e_usuario(monkeypatch):
    assert keycloak_admin._first_id([{"id": "1"}]) == "1"
    assert keycloak_admin._first_id([]) is None

    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda *_args, **_kwargs: (200, [{"id": "user-1"}], {}),
    )

    assert keycloak_admin._find_user_id("token", "user@example.com") == "user-1"


def test_garante_role_existente_ou_cria(monkeypatch):
    chamadas = []

    def fake_request(method, url, **kwargs):
        chamadas.append((method, url, kwargs))
        if len(chamadas) == 1:
            return 404, None, {}
        if len(chamadas) == 2:
            return 201, None, {}
        return 200, {"name": "caixa"}, {}

    monkeypatch.setattr(keycloak_admin, "_request", fake_request)

    assert keycloak_admin._ensure_realm_role("token", "caixa") == {"name": "caixa"}
    assert chamadas[1][0] == "POST"


def test_garante_role_retorna_existente(monkeypatch):
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda *_args, **_kwargs: (200, {"name": "admin"}, {}),
    )

    assert keycloak_admin._ensure_realm_role("token", "admin") == {"name": "admin"}


def test_reset_password_e_assign_role(monkeypatch):
    chamadas = []
    monkeypatch.setattr(keycloak_admin, "_ensure_realm_role", lambda _token, role: {"name": role})
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda method, url, **kwargs: chamadas.append((method, url, kwargs)) or (204, None, {}),
    )

    keycloak_admin._reset_password("token", "user-1", "senha")
    keycloak_admin._assign_realm_role("token", "user-1", "caixa")

    assert chamadas[0][0] == "PUT"
    assert chamadas[0][2]["data"]["value"] == "senha"
    assert chamadas[1][0] == "POST"
    assert chamadas[1][2]["data"] == [{"name": "caixa"}]


def test_create_keycloak_user_desligado(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", False)

    assert keycloak_admin.create_keycloak_user(
        nome="Teste",
        email="teste@example.com",
        senha="senha",
        nome_role="caixa",
    ) == (None, False)


def test_create_keycloak_user_existente(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    monkeypatch.setattr(keycloak_admin, "_admin_token", lambda: "token")
    monkeypatch.setattr(keycloak_admin, "_find_user_id", lambda _token, _email: "user-1")
    monkeypatch.setattr(keycloak_admin, "_reset_password", lambda *_args: None)
    monkeypatch.setattr(keycloak_admin, "_assign_realm_role", lambda *_args: None)

    assert keycloak_admin.create_keycloak_user(
        nome="Teste",
        email="teste@example.com",
        senha="senha",
        nome_role="caixa",
    ) == ("user-1", False)


def test_create_keycloak_user_novo_com_location(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    monkeypatch.setattr(keycloak_admin, "_admin_token", lambda: "token")
    monkeypatch.setattr(keycloak_admin, "_find_user_id", lambda _token, _email: None)
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda *_args, **_kwargs: (
            201,
            None,
            {"Location": "http://keycloak/admin/realms/x/users/user-2"},
        ),
    )
    monkeypatch.setattr(keycloak_admin, "_reset_password", lambda *_args: None)
    monkeypatch.setattr(keycloak_admin, "_assign_realm_role", lambda *_args: None)

    assert keycloak_admin.create_keycloak_user(
        nome="Teste",
        email="novo@example.com",
        senha="senha",
        nome_role="caixa",
    ) == ("user-2", True)


def test_create_keycloak_user_falha_sem_id(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    monkeypatch.setattr(keycloak_admin, "_admin_token", lambda: "token")
    monkeypatch.setattr(keycloak_admin, "_find_user_id", lambda _token, _email: None)
    monkeypatch.setattr(keycloak_admin, "_request", lambda *_args, **_kwargs: (201, None, {}))

    with pytest.raises(HTTPException) as exc_info:
        keycloak_admin.create_keycloak_user(
            nome="Teste",
            email="novo@example.com",
            senha="senha",
            nome_role="caixa",
        )

    assert exc_info.value.detail == "Keycloak nao retornou o ID do usuario criado"


def test_update_keycloak_user_atualiza_campos_senha_e_role(monkeypatch):
    chamadas = []
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    monkeypatch.setattr(keycloak_admin, "_admin_token", lambda: "token")
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda method, url, **kwargs: chamadas.append((method, url, kwargs)) or (204, None, {}),
    )
    monkeypatch.setattr(
        keycloak_admin,
        "_reset_password",
        lambda *args: chamadas.append(("reset", args, {})),
    )
    monkeypatch.setattr(
        keycloak_admin,
        "_assign_realm_role",
        lambda *args: chamadas.append(("role", args, {})),
    )

    keycloak_admin.update_keycloak_user(
        "user-1",
        nome="Novo Nome",
        email="novo@example.com",
        senha="senha",
        nome_role="cozinha",
    )

    assert chamadas[0][0] == "PUT"
    assert chamadas[0][2]["data"]["username"] == "novo@example.com"
    assert chamadas[1][0] == "reset"
    assert chamadas[2][0] == "role"


def test_update_keycloak_user_ignora_sem_sync_ou_sem_id(monkeypatch):
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", False)

    assert keycloak_admin.update_keycloak_user("user-1", nome="Teste") is None

    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    assert keycloak_admin.update_keycloak_user(None, nome="Teste") is None


def test_delete_keycloak_user(monkeypatch):
    chamadas = []
    monkeypatch.setattr(keycloak_admin.settings, "keycloak_user_sync_enabled", True)
    monkeypatch.setattr(keycloak_admin, "_admin_token", lambda: "token")
    monkeypatch.setattr(
        keycloak_admin,
        "_request",
        lambda method, url, **kwargs: chamadas.append((method, url, kwargs)) or (204, None, {}),
    )

    keycloak_admin.delete_keycloak_user("user-1")

    assert chamadas[0][0] == "DELETE"
    assert chamadas[0][2]["expected_statuses"] == (204, 404)
