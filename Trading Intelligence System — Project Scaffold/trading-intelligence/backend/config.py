"""Application configuration using Pydantic Settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development")
    app_log_level: str = Field(default="INFO")
    app_secret_key: str = Field(default="change-me")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://tis_user:password@localhost:5432/trading_intel"
    )
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="tis_user")
    postgres_password: str = Field(default="password")
    postgres_db: str = Field(default="trading_intel")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Telegram
    telegram_bot_token: str = Field(default="")
    telegram_allowed_user_ids: str = Field(default="")

    # Tailscale
    tailscale_ip: str = Field(default="127.0.0.1")

    # AI — Local
    ollama_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5:7b")
    ollama_embed_model: str = Field(default="nomic-embed-text")

    # AI — Cloud (optional)
    openai_api_key: str = Field(default="")
    gemini_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    xai_api_key: str = Field(default="")

    # Economic Data APIs
    fred_api_key: str = Field(default="")
    bea_api_key: str = Field(default="")
    bls_api_key: str = Field(default="")

    # Crypto Data
    coingecko_api_key: str = Field(default="")

    # Budget
    monthly_ai_budget: float = Field(default=50.0)

    # Backup
    backup_dir: str = Field(default="/opt/trading-intelligence/backups")
    backup_retention_days: int = Field(default=7)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def allowed_user_ids(self) -> list[int]:
        if not self.telegram_allowed_user_ids:
            return []
        return [
            int(uid.strip())
            for uid in self.telegram_allowed_user_ids.split(",")
            if uid.strip().isdigit()
        ]


settings = Settings()
