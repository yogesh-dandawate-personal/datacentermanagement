from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings"""
    app_title: str = "NetZero API"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database URL - read from DATABASE_URL env variable, fallback to localhost
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/netzero")

    # Connection pool configuration for production
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    database_pool_max_overflow: int = int(os.getenv("DATABASE_POOL_MAX_OVERFLOW", "40"))
    database_pool_pre_ping: bool = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true"

    secret_key: str = "change-me-in-production"

    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "netzero"
    keycloak_client_id: str = "netzero-api"

    class Config:
        env_file = ".env"

settings = Settings()
