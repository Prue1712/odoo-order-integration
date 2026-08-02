from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    odoo_url: str = "http://localhost:8069"
    odoo_db: str = "odoo18"
    odoo_user: str = "admin"
    odoo_password: str = "admin"

    database_url: str = (
        "postgresql+psycopg://integration:integration@localhost:5433/integration"
    )


def get_settings() -> Settings:
    """Lee .env en cada llamada (evita credenciales viejas en memoria)."""
    load_dotenv(ENV_FILE, override=True)
    return Settings()


# compatibilidad con imports existentes
settings = get_settings()
