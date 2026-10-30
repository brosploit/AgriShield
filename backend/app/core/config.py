"""AgriShield AI - Core Configuration

Loads application settings using Pydantic v2 Settings.
Supports environment variables and .env file loading.
"""

from typing import List, Union
import json
from pathlib import Path
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgriShield AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database connection string
    # Defaults to local PostgreSQL, supports SQLite for testing
    DATABASE_URL: str = "postgresql+psycopg2://postgres@127.0.0.1:5433/agrishield"
    TEST_DATABASE_URL: str = "sqlite:///./test_agrishield.db"

    # Security & JWT Tokens
    SECRET_KEY: str = "agrishield-dev-secret-key-32-chars-long-secure-hash-token"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # AI & ML Engine
    MODEL_VERSION: str = "1.0.0-baseline"
    ML_MODEL_PATH: str = "ml/models"

    # Storage Verification
    STORAGE_HASH_SALT: str = "agrishield-grain-verification-salt-2026"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

