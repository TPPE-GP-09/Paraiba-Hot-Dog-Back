import json
from urllib.error import URLError

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from src import security


class FakeResponse:
    """Resposta HTTP fake usada para simular o endpoint JWKS do Keycloak."""

    def __init__(self, body: str, status: int = 200):
        """Guarda corpo, status e headers da resposta simulada."""
        self.body = body
        self.status = status
        self.headers = {"content-type": "application/json"}

    def __enter__(self):
        """Permite usar a resposta fake em um bloco with."""
        return self

    def __exit__(self, *args):
        """Finaliza o contexto sem suprimir excecoes."""
        return False

    def read(self) -> bytes:
        """Retorna o corpo fake em bytes, como urlopen faria."""
        return self.body.encode("utf-8")


@pytest.fixture(autouse=True)
def clear_jwks_cache():
    """Limpa o cache de JWKS antes e depois de cada teste."""
    security._jwks_cache["keys"] = None
    security._jwks_cache["expires_at"] = 0.0
    yield
    security._jwks_cache["keys"] = None
    security._jwks_cache["expires_at"] = 0.0


def test_fetch_jwks_busca_e_usa_cache(monkeypatch):
    """Garante que o JWKS e buscado uma vez e reutilizado pelo cache."""
    chamadas = {"total": 0}

    def fake_urlopen(_url, timeout):
        """Simula a resposta do endpoint de chaves publicas."""
        chamadas["total"] += 1
        assert timeout == 5
        return FakeResponse(json.dumps({"keys": [{"kid": "abc"}]}))

    monkeypatch.setattr(security, "urlopen", fake_urlopen)

    assert security._fetch_jwks() == {"keys": [{"kid": "abc"}]}
    assert security._fetch_jwks() == {"keys": [{"kid": "abc"}]}
    assert chamadas["total"] == 1


def test_fetch_jwks_falha_quando_keycloak_indisponivel(monkeypatch):
    """Valida o erro retornado quando o Keycloak nao responde."""
    def fake_urlopen(_url, timeout):
        """Simula indisponibilidade de rede ao buscar o JWKS."""
        raise URLError("fora")

    monkeypatch.setattr(security, "urlopen", fake_urlopen)

    with pytest.raises(HTTPException) as exc_info:
        security._fetch_jwks()

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Nao foi possivel consultar as chaves do Keycloak"


def test_fetch_jwks_falha_com_json_invalido(monkeypatch):
    """Valida o erro retornado quando o JWKS nao e JSON valido."""
    monkeypatch.setattr(security, "urlopen", lambda _url, timeout: FakeResponse("{"))

    with pytest.raises(HTTPException) as exc_info:
        security._fetch_jwks()

    assert exc_info.value.detail == "Resposta invalida das chaves do Keycloak"


def test_get_signing_key_retorna_chave_do_kid(monkeypatch):
    """Garante que a chave correta e escolhida pelo kid do token."""
    monkeypatch.setattr(security.jwt, "get_unverified_header", lambda _token: {"kid": "key-1"})
    monkeypatch.setattr(
        security,
        "_fetch_jwks",
        lambda: {"keys": [{"kid": "key-1", "alg": "RS256"}]},
    )

    assert security._get_signing_key("token") == {"kid": "key-1", "alg": "RS256"}


def test_get_signing_key_rejeita_token_sem_kid(monkeypatch):
    """Valida rejeicao de token sem identificador de chave."""
    monkeypatch.setattr(security.jwt, "get_unverified_header", lambda _token: {})

    with pytest.raises(HTTPException) as exc_info:
        security._get_signing_key("token")

    assert exc_info.value.detail == "Token sem identificador de chave"


def test_get_signing_key_rejeita_token_com_header_invalido(monkeypatch):
    """Valida rejeicao de token com header JWT invalido."""
    def fake_header(_token):
        """Simula erro ao ler o header do JWT."""
        raise JWTError("invalido")

    monkeypatch.setattr(security.jwt, "get_unverified_header", fake_header)

    with pytest.raises(HTTPException) as exc_info:
        security._get_signing_key("token")

    assert exc_info.value.detail == "Token invalido"


def test_get_signing_key_rejeita_chave_nao_encontrada(monkeypatch):
    """Valida erro quando o kid do token nao existe no JWKS."""
    monkeypatch.setattr(security.jwt, "get_unverified_header", lambda _token: {"kid": "a"})
    monkeypatch.setattr(security, "_fetch_jwks", lambda: {"keys": [{"kid": "b"}]})

    with pytest.raises(HTTPException) as exc_info:
        security._get_signing_key("token")

    assert exc_info.value.detail == "Chave de assinatura do token nao encontrada"


def test_extract_roles_normaliza_roles_de_realm_e_clients():
    """Garante que roles de realm e clients sao combinadas sem duplicidade."""
    payload = {
        "realm_access": {"roles": ["caixa", "dashboard"]},
        "resource_access": {
            "api": {"roles": ["dashboard", "configuracoes"]},
            "outro": {"roles": ["cozinha"]},
        },
    }

    assert security._extract_roles(payload) == [
        "caixa",
        "configuracoes",
        "cozinha",
        "dashboard",
    ]


def test_decode_keycloak_token_valida_payload_e_client(monkeypatch):
    """Valida decode de token emitido para o client esperado."""
    monkeypatch.setattr(security, "_get_signing_key", lambda _token: {"alg": "RS256"})
    monkeypatch.setattr(security.settings, "keycloak_client_id", "paraiba-hotdog-api")

    def fake_decode(*_args, **_kwargs):
        """Simula payload valido retornado pela biblioteca JWT."""
        return {
            "azp": "paraiba-hotdog-api",
            "realm_access": {"roles": ["administrador"]},
        }

    monkeypatch.setattr(security.jwt, "decode", fake_decode)

    payload = security.decode_keycloak_token("token")

    assert payload["roles"] == ["administrador"]


def test_decode_keycloak_token_rejeita_client_errado(monkeypatch):
    """Garante rejeicao de token emitido para outro client."""
    monkeypatch.setattr(security, "_get_signing_key", lambda _token: {"alg": "RS256"})
    monkeypatch.setattr(security.settings, "keycloak_client_id", "paraiba-hotdog-api")
    monkeypatch.setattr(security.jwt, "decode", lambda *_args, **_kwargs: {"azp": "outro"})

    with pytest.raises(HTTPException) as exc_info:
        security.decode_keycloak_token("token")

    assert exc_info.value.detail == "Token emitido para outro cliente"


def test_decode_keycloak_token_rejeita_jwt_error(monkeypatch):
    """Garante que falhas de validacao JWT viram erro 401."""
    monkeypatch.setattr(security, "_get_signing_key", lambda _token: {"alg": "RS256"})

    def fake_decode(*_args, **_kwargs):
        """Simula erro de token expirado ou invalido."""
        raise JWTError("expirado")

    monkeypatch.setattr(security.jwt, "decode", fake_decode)

    with pytest.raises(HTTPException) as exc_info:
        security.decode_keycloak_token("token")

    assert exc_info.value.detail == "Token invalido ou expirado"


def test_get_current_user_valida_header_bearer(monkeypatch):
    """Garante que a dependencia extrai e valida o token Bearer."""
    monkeypatch.setattr(security, "decode_keycloak_token", lambda token: {"sub": token})
    credenciais = HTTPAuthorizationCredentials(scheme="Bearer", credentials="abc")

    assert security.get_current_user(credenciais) == {"sub": "abc"}


def test_get_current_user_rejeita_ausente_ou_esquema_invalido():
    """Valida rejeicao de requisicao sem Bearer token valido."""
    with pytest.raises(HTTPException):
        security.get_current_user(None)

    credenciais = HTTPAuthorizationCredentials(scheme="Basic", credentials="abc")
    with pytest.raises(HTTPException):
        security.get_current_user(credenciais)


def test_require_roles_permite_intersecao_e_bloqueia_sem_role():
    """Garante que a dependencia de roles permite e bloqueia corretamente."""
    dependencia = security.require_roles("administrador", "caixa")

    assert dependencia(user={"roles": ["caixa"]}) == {"roles": ["caixa"]}

    with pytest.raises(HTTPException) as exc_info:
        dependencia(user={"roles": ["cozinha"]})

    assert exc_info.value.status_code == 403
