from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with safe local defaults.

    The project deliberately defaults to a local deterministic model provider and a
    SQLite database so that the demo is runnable without third-party credentials.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "EvidenceOps API"
    environment: Literal["development", "test", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./evidenceops.db"
    cors_origins: str = "http://localhost:3000"
    default_tenant_id: str = "demo-tenant"

    enable_remote_model: bool = False
    openai_compatible_base_url: str = "https://api.openai.com/v1"
    openai_compatible_api_key: str = ""
    openai_compatible_model: str = ""

    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "evidenceops-api"
    store_redacted_trace_payloads: bool = True

    maximum_retrieval_documents: int = Field(default=8, ge=1, le=20)
    human_review_required: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def data_root(self) -> Path:
        return self.backend_root / "data"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
