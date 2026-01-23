from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # TODO: Define your configuration settings
    # Consider:
    # - Database connection URL
    # - JWT secret key and algorithm
    # - CORS origins
    # - Logging configuration

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = False
    )


settings = Settings()
