"""Centralized application configuration.

TODO: Expand as real features land (e.g. max upload size, allowed
file extensions, scoring weights). Keep this the single source of
truth for configuration — do not read os.environ elsewhere.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    debug: bool = True

    host: str = "0.0.0.0"
    port: int = 8000

    cors_origins: str = "http://localhost:5173"

    datasets_raw_dir: str = "../datasets/raw"
    datasets_cleaned_dir: str = "../datasets/cleaned"
    outputs_dir: str = "../outputs"

    # Upload limits (Phase 1). Revisit if bigger files are needed later.
    max_upload_size_mb: int = 50
    allowed_upload_extensions: set[str] = Field(default_factory=lambda: {"csv", "xlsx"})

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
