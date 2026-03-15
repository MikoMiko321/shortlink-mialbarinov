import os

from pydantic import BaseModel


class Settings(BaseModel):
    # database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/shortlinks"
    # redis_url: str = "redis://redis:6379"

    database_url: str = os.getenv("DATABASE_URL")
    redis_url: str = os.getenv("REDIS_URL")
    base_url: str = "http://localhost:8000"
    default_link_ttl_days: int = 30


settings = Settings()
