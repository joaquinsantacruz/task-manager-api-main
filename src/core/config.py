from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from typing import List

class Settings(BaseSettings):
    """Application settings"""

    # TODO: Define your configuration settings
    # Consider:
    # - Logging configuration

    PROJECT_NAME: str = "Task Manager API"
    API_V1_STR: str = "/api/v1"

     # - Database connection URL
    DATABASE_URL: PostgresDsn

    # - JWT secret key and algorithm
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # - CORS origins
    CORS_ORIGINS: List[str] = []
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False,
        extra="ignore"
    )


settings = Settings()
