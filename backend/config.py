from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DB_HOST:     str  = "localhost"
    DB_PORT:     int  = 3306
    DB_NAME:     str  = "jobpilot"
    DB_USER:     str  = "root"
    DB_PASSWORD: str  = "jobpilot123"
    OLLAMA_URL:  str  = "http://localhost:11434"
    SECRET_KEY:  str  = "changeme-in-production"
    DEBUG:       bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
