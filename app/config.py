from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "rocket-db"
    POSTGRES_USER: str = "rocket-user"
    POSTGRES_PASSWORD: str = "R0ck3t4rt1cl35"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL_SECONDS: int = 90
    CACHE_PREFIX: str = "article:"
    API_KEY: str | None = "47da9ef4-0a22-4625-89f3-ef7025a64192"
    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> "Settings":
    return Settings()
