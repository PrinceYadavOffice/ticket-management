"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root: src/backend/app/core/config.py → parents[4]
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ENV_FILE = _REPO_ROOT / ".env"
_DATA_DIR = _REPO_ROOT / "data"
_DEFAULT_DB_PATH = _DATA_DIR / "tickets.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{_DEFAULT_DB_PATH}"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_data_dir(self) -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_data_dir()
