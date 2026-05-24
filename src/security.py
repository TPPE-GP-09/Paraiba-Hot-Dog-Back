import json
from time import monotonic
from typing import Any, Callable
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict[str, Any] = {"keys": None, "expires_at": 0.0}


def _auth_exception(detail: str = "Credenciais invalidas") -> HTTPException:
    """Cria uma resposta 401 padronizada para falhas de autenticacao Bearer."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )t

def _fetch_jwks() -> dict[str, Any]:
    """Busca e guarda em cache as chaves publicas JWKS publicadas pelo Keycloak."""
    now = monotonic()
    cached_keys = _jwks_cache["keys"]
    if cached_keys and now < _jwks_cache["expires_at"]:
        return cached_keys

    try:
        with urlopen(settings.keycloak_jwks_url, timeout=5) as response:
            jwks = response.read().decode("utf-8")
    except (TimeoutError, URLError) as exc:
        raise _auth_exception(
            "Nao foi possivel consultar as chaves do Keycloak"
        ) from exc

    try:
        keys = json.loads(jwks)
    except json.JSONDecodeError as exc:
        raise _auth_exception("Resposta invalida das chaves do Keycloak") from exc
    _jwks_cache["keys"] = keys
    _jwks_cache["expires_at"] = now + settings.keycloak_jwks_cache_seconds
    return keys


def _get_signing_key(token: str) -> dict[str, Any]:
    """Seleciona no JWKS a chave publica usada para assinar o token recebido."""
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise _auth_exception("Token invalido") from exc

    token_kid = header.get("kid")
    if not token_kid:
        raise _auth_exception("Token sem identificador de chave")

    for key in _fetch_jwks().get("keys", []):
        if key.get("kid") == token_kid:
            return key

    raise _auth_exception("Chave de assinatura do token nao encontrada")


def _extract_roles(payload: dict[str, Any]) -> list[str]:
    """Extrai roles de realm e clients do payload JWT validado."""
    roles: set[str] = set()
    roles.update(payload.get("realm_access", {}).get("roles", []))

    # pega roles de todos os clientes, pois o token pode conter permissoes
    # de mais de um cliente dependendo da configuracao do Keycloak
    resource_access = payload.get("resource_access", {})
    for client_data in resource_access.values():
        roles.update(client_data.get("roles", []))

    return sorted(roles)


def decode_keycloak_token(token: str) -> dict[str, Any]:
    """Valida o JWT do Keycloak e retorna o payload com as roles normalizadas."""
    key = _get_signing_key(token)
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            issuer=settings.keycloak_issuer,
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise _auth_exception("Token invalido ou expirado") from exc

    if settings.keycloak_client_id:
        authorized_party = payload.get("azp")
        audience = payload.get("aud", [])
        if isinstance(audience, str):
            audience = [audience]
        if settings.keycloak_client_id not in [authorized_party, *audience]:
            raise _auth_exception("Token emitido para outro cliente")

    payload["roles"] = _extract_roles(payload)
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """Dependencia FastAPI que exige token Bearer valido e retorna o usuario atual."""
    if credentials is None:
        raise _auth_exception("Token de autenticacao ausente")

    if credentials.scheme.lower() != "bearer":
        raise _auth_exception("Esquema de autenticacao invalido")

    return decode_keycloak_token(credentials.credentials)


def require_roles(*required_roles: str) -> Callable[..., dict[str, Any]]:
    """Cria uma dependencia FastAPI que exige pelo menos uma das roles informadas."""
    def dependency(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        """Valida se o usuario autenticado possui alguma role exigida."""
        user_roles = set(user.get("roles", []))
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sem permissao para acessar este recurso",
            )
        return user

    return dependency
