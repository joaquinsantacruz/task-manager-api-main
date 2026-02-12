from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from typing import List
import json

class Settings(BaseSettings):
    """Application settings"""

    PROJECT_NAME: str = "Task Manager API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: PostgresDsn
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_TIMEOUT: int = 30

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ""
    
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        raw = self.CORS_ORIGINS.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                value = json.loads(raw)
                return [item for item in value if isinstance(item, str) and item.strip()]
            except json.JSONDecodeError:
                return []
        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings()
