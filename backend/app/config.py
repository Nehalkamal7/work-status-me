import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    APP_NAME: str = "Enterprise Work Status & Sync Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database URL: default to local sqlite+aiosqlite database or PostgreSQL asyncpg
    DATABASE_URL: str = "sqlite+aiosqlite:///./work_status.db"
    
    # Security
    JWT_SECRET: str = "super-secret-enterprise-jwt-key-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Valid 32-byte url-safe base64-encoded Fernet key
    FERNET_KEY: str = "J1dOODNlNWk2Nzdiazh2OWFzZDFmZ2hpamtsbW5vcHE="

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_fernet_key(self) -> bytes:
        if self.FERNET_KEY and len(self.FERNET_KEY) == 44:
            return self.FERNET_KEY.encode()
        # Reproducible valid base64 32-byte Fernet key
        return b"J1dOODNlNWk2Nzdiazh2OWFzZDFmZ2hpamtsbW5vcHE="

settings = Settings()
