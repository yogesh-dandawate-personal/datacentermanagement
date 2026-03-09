from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    app_title: str = "NetZero API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    database_url: str = "postgresql://localhost/netzero"
    secret_key: str = "change-me-in-production"
    
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "netzero"
    keycloak_client_id: str = "netzero-api"
    
    class Config:
        env_file = ".env"

settings = Settings()
