import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from src.config import settings


def _request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    data: dict[str, Any] | list[Any] | None = None,
    form: dict[str, str] | None = None,
    expected_statuses: tuple[int, ...] = (200,),
) -> tuple[int, Any, dict[str, str]]:
    """Executa uma requisicao HTTP generica ao Keycloak e retorna (status, body, headers).

    Lanca HTTPException para status fora de expected_statuses ou em caso de falha de rede.
    """
    headers: dict[str, str] = {}
    body: bytes | None = None

    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    if form is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urlencode(form).encode("utf-8")

    request = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body) if response_body else None
            return response.status, parsed, dict(response.headers)
    except HTTPError as erro:
        response_body = erro.read().decode("utf-8")
        conteudo = json.loads(response_body) if response_body else None
        if erro.code in expected_statuses:
            return erro.code, conteudo, dict(erro.headers)
        raise _keycloak_exception(erro.code) from erro
    except (TimeoutError, URLError) as erro:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nao foi possivel conectar ao Keycloak",
        ) from erro


def _keycloak_exception(status_code: int) -> HTTPException:
    """Mapeia um codigo de status HTTP do Keycloak para uma HTTPException adequada."""
    if status_code == 409:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuario ja cadastrado no Keycloak",
        )
    if status_code in {401, 403}:
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Credenciais administrativas do Keycloak invalidas",
        )
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Falha ao consultar o Keycloak: HTTP {status_code}",
    )


def _realm_admin_url(path: str) -> str:
    """Constroi a URL completa para um endpoint da Admin API do realm configurado."""
    base_url = settings.keycloak_admin_base_url.rstrip("/")
    return f"{base_url}/admin/realms/{settings.keycloak_realm}/{path.lstrip('/')}"


def _admin_token() -> str:
    """Obtem um token de acesso administrativo do realm master do Keycloak."""
    base_url = settings.keycloak_admin_base_url.rstrip("/")
    _, body, _ = _request(
        "POST",
        f"{base_url}/realms/master/protocol/openid-connect/token",
        form={
            "client_id": "admin-cli",
            "username": settings.keycloak_admin_username,
            "password": settings.keycloak_admin_password,
            "grant_type": "password",
        },
    )
    return body["access_token"]


def _first_id(items: Any) -> str | None:
    """Retorna o campo 'id' do primeiro elemento de uma lista, ou None se vazia."""
    if isinstance(items, list) and items:
        return items[0].get("id")
    return None


def _find_user_id(token: str, email: str) -> str | None:
    """Busca no Keycloak o ID de um usuario pelo e-mail exato; retorna None se nao encontrado."""
    query = urlencode({"email": email, "exact": "true"})
    _, body, _ = _request("GET", _realm_admin_url(f"users?{query}"), token=token)
    return _first_id(body)


def _ensure_realm_role(token: str, role_name: str) -> dict[str, Any]:
    """Garante que a role de realm existe no Keycloak, criando-a se necessario, e a retorna."""
    role_status, role, _ = _request(
        "GET",
        _realm_admin_url(f"roles/{role_name}"),
        token=token,
        expected_statuses=(200, 404),
    )
    if role_status == 200:
        return role

    _request(
        "POST",
        _realm_admin_url("roles"),
        token=token,
        data={"name": role_name, "description": "Role sincronizada pela API"},
        expected_statuses=(201, 409),
    )
    _, role, _ = _request("GET", _realm_admin_url(f"roles/{role_name}"), token=token)
    return role


def _reset_password(token: str, user_id: str, senha: str) -> None:
    """Redefine a senha de um usuario no Keycloak de forma nao temporaria."""
    _request(
        "PUT",
        _realm_admin_url(f"users/{user_id}/reset-password"),
        token=token,
        data={"type": "password", "value": senha, "temporary": False},
        expected_statuses=(204,),
    )


def _assign_realm_role(token: str, user_id: str, role_name: str) -> None:
    """Atribui uma role de realm ao usuario informado, criando a role se necessario."""
    role = _ensure_realm_role(token, role_name)
    _request(
        "POST",
        _realm_admin_url(f"users/{user_id}/role-mappings/realm"),
        token=token,
        data=[role],
        expected_statuses=(204,),
    )


def create_keycloak_user(
    *,
    nome: str,
    email: str,
    senha: str,
    nome_role: str,
) -> tuple[str | None, bool]:
    """Cria ou localiza um usuario no Keycloak, define sua senha e atribui a role informada.

    Retorna uma tupla (keycloak_id, criado), onde 'criado' indica se o usuario foi recem criado.
    Retorna (None, False) se a sincronizacao com o Keycloak estiver desabilitada.
    """
    if not settings.keycloak_user_sync_enabled:
        return None, False

    token = _admin_token()
    user_id = _find_user_id(token, email)
    created = False

    if user_id is None:
        _, _, headers = _request(
            "POST",
            _realm_admin_url("users"),
            token=token,
            data={
                "username": email,
                "email": email,
                "firstName": nome,
                "emailVerified": True,
                "enabled": True,
            },
            expected_statuses=(201, 409),
        )
        if headers.get("Location"):
            user_id = headers["Location"].rstrip("/").split("/")[-1]
        else:
            user_id = _find_user_id(token, email)
        created = True

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Keycloak nao retornou o ID do usuario criado",
        )

    _reset_password(token, user_id, senha)
    _assign_realm_role(token, user_id, nome_role)

    return user_id, created


def update_keycloak_user(
    user_id: str | None,
    *,
    nome: str | None = None,
    email: str | None = None,
    senha: str | None = None,
    nome_role: str | None = None,
) -> None:
    """Atualiza dados (nome, e-mail, senha e/ou role) de um usuario existente no Keycloak.

    Campos passados como None sao ignorados. Nao faz nada se a sincronizacao estiver
    desabilitada ou se user_id for None.
    """
    if not settings.keycloak_user_sync_enabled or not user_id:
        return

    token = _admin_token()
    if nome is not None or email is not None:
        payload: dict[str, Any] = {"enabled": True}
        if nome is not None:
            payload["firstName"] = nome
        if email is not None:
            payload["email"] = email
            payload["username"] = email
            payload["emailVerified"] = True
        _request(
            "PUT",
            _realm_admin_url(f"users/{user_id}"),
            token=token,
            data=payload,
            expected_statuses=(204,),
        )

    if senha is not None:
        _reset_password(token, user_id, senha)

    if nome_role is not None:
        _assign_realm_role(token, user_id, nome_role)


def delete_keycloak_user(user_id: str | None) -> None:
    """Remove um usuario do Keycloak pelo seu ID.

    Nao faz nada se a sincronizacao estiver desabilitada ou se user_id for None.
    """
    if not settings.keycloak_user_sync_enabled or not user_id:
        return

    token = _admin_token()
    _request(
        "DELETE",
        _realm_admin_url(f"users/{user_id}"),
        token=token,
        expected_statuses=(204, 404),
    )
