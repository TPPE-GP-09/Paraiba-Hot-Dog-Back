from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "paraiba_hotdog_db"
    database_url: str | None = None
    whatsapp_token: str = ""
    phone_number_id: str = ""
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
