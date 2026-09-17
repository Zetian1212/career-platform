from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Career Platform"
    database_url: str = "sqlite:///./career_platform.db"
    admin_username: str = "admin"
    admin_password: str = "change-me"
    session_secret: str = "change-this-secret"
    fallback_profile_path: str = "app/static/fallback/profile.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()
