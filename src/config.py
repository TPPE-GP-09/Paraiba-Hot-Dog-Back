from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "paraiba_hotdog_db"
    database_url: str | None = None
    twilio_account_sid: str = ""
    twilio_api_key_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
    keycloak_realm: str = "paraiba-hotdog"
    keycloak_issuer: str = "http://localhost:8080/realms/paraiba-hotdog"
    keycloak_jwks_url: str = (
        "http://keycloak:8080/realms/paraiba-hotdog/protocol/openid-connect/certs"
    )
    keycloak_client_id: str | None = None
    keycloak_jwks_cache_seconds: int = 3600
    keycloak_admin_base_url: str = "http://localhost:8080"
    keycloak_admin_username: str = "admin"
    keycloak_admin_password: str = "admin"
    keycloak_user_sync_enabled: bool = True
    frontend_base_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
        frontend_origin = self.frontend_base_url.strip().rstrip("/")
        if frontend_origin:
            origins.append(frontend_origin)
        return list(dict.fromkeys(origins))


settings = Settings()
