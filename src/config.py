from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
