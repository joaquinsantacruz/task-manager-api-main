"""
Test configuration module.

This module provides configuration settings specifically for testing,
including test database setup and test-specific environment variables.
Following the Single Responsibility Principle - handles only test configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class TestSettings(BaseSettings):
    """
    Test-specific configuration settings.
    
    Inherits from BaseSettings to leverage Pydantic's validation and
    environment variable handling. Uses a separate test database to
    ensure isolation from development/production data.
    """
    
    # Test database configuration
    # Uses a separate database with '_test' suffix for isolation
    TEST_DATABASE_URL: PostgresDsn = "postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskmanager_test"
    
    # JWT configuration for testing
    SECRET_KEY: str = "test-secret-key-for-testing-only-do-not-use-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Manager API - Test"
    
    model_config = SettingsConfigDict(
        env_file=".env.test",
        case_sensitive=False,
        extra="ignore"
    )


# Global test settings instance
test_settings = TestSettings()
