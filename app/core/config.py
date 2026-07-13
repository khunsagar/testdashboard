"""
Central app configuration, loaded from environment variables (.env in local dev).

Step 3: fill in real values and confirm `get_settings().database_url`
actually connects to Postgres before moving on.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    log_level: str = "INFO"

    # Database — PLACEHOLDER default is SQLite so the app runs with ZERO setup.
    # Step 3: point this at real Postgres via .env:
    #   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/test_control
    database_url: str = "sqlite:///./local_dev.db"

    # Redis (Step 3, if in scope for this service)
    redis_url: str = "redis://localhost:6379/0"

    # Auth (Phase 2)
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # GitHub integration (Phase 6)
    github_client_id: str = ""
    github_client_secret: str = ""
    github_webhook_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
