"""
app/config.py — Centralised settings via pydantic-settings.
All env vars are validated at startup; the app fails fast if anything is missing.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    
    database_url: str = "postgresql+asyncpg://cip_user:password@localhost:5433/worldlink_cip"
    database_url_sync: str = "postgresql://cip_user:password@localhost:5433/worldlink_cip"

    
    redis_url: str = "redis://localhost:6379/0"

    
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "cip_plans"

    
    groq_api_key: str = ""
    groq_llm_model: str = "llama-3.1-8b-instant"
    groq_llm_model_large: str = "llama-3.1-70b-versatile"

   
    embedding_model: str = "all-MiniLM-L6-v2"

   
    slack_webhook_url: str = ""
    alert_email: str = "intel@worldlink.com.np"

    
    app_port: int = 8000
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me"

    worldlink_slug: str = "worldlink"

    
    scraper_concurrency: int = 3
    scraper_retry_attempts: int = 3
    scraper_timeout_ms: int = 30_000
    scraper_headless: bool = True

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
