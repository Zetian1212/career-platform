from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_POSTGRES_PREFIXES = ('postgres://', 'postgresql://')


def normalize_database_url(url: str) -> str:
    """Pin Postgres URLs to psycopg 3; Railway hands out plain postgresql:// URLs."""
    for prefix in _POSTGRES_PREFIXES:
        if url.startswith(prefix):
            return 'postgresql+psycopg://' + url[len(prefix):]
    return url


class Settings(BaseSettings):
    app_name: str = "Career Platform"
    database_url: str = "sqlite:///./career_platform.db"
    fallback_profile_path: str = "app/static/fallback/profile.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator('database_url')
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        return normalize_database_url(value)


def get_settings() -> Settings:
    return Settings()
