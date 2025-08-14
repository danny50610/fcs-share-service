import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: str = ''
    redis_url: str = ''
    API_URL: str = 'http://127.0.0.1:8000'
    SECRET_KEY: str = secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
