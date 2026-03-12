"""AegisNet configuration — loads from .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Local Model
    ollama_base_url: str = "http://localhost:11434"

    # Routing
    default_routing_strategy: str = "auto"
    default_model: str = "local/llama3"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/aegisnet"
    redis_url: str = "redis://localhost:6379/0"

    # Security
    api_secret_key: str = "change-me-to-a-random-secret"
    default_api_key: str = "ag-1234567890"  # For demo / development

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
