from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://pqshield:pqshield@localhost:5432/pqshield"
    frontend_origin: str = Field(default="http://localhost:5173")
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "pqshield"
    mqtt_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        origins = []
        for origin in self.frontend_origin.split(","):
            origin = origin.strip().rstrip("/")
            if origin and not origin.startswith(("http://", "https://")):
                origin = f"https://{origin}"
            if origin:
                origins.append(origin)
        return origins

    @property
    def sqlalchemy_database_url(self) -> str:
        # Render supplies PostgreSQL URLs using the generic postgres:// scheme.
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
