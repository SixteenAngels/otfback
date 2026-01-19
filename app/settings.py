from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Development: SQLite, Production: PostgreSQL (from environment)
    database_url: str = "sqlite+aiosqlite:///./test_concert.db"
    env: str = "development"
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()

# Override with production settings if ENV is production
if settings.env == "production":
    # Production uses PostgreSQL from DATABASE_URL environment variable
    # Make sure to set: DATABASE_URL, SECRET_KEY in production environment
    pass
