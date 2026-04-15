from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "GenReader"
    env: Literal["development", "production", "test"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    demo_user_email: str = "demo@genreader.local"
    demo_user_password: str = "demo"
    demo_user_name: str = "Demo User"

    database_url: str = "sqlite+aiosqlite:///./genreader.db"
    redis_url: str = "redis://localhost:6379/0"

    storage_backend: Literal["minio", "local"] = "local"
    storage_local_path: str = "./storage"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "genreader"
    minio_secure: bool = False

    vlm_provider: Literal["qwen-vl-local", "openai", "stub"] = "stub"
    vlm_model: str = "Qwen/Qwen2-VL-2B-Instruct"
    vlm_device: str = "cpu"
    vlm_max_new_tokens: int = 1024
    vlm_timeout_s: int = 120

    rate_limit_per_minute: int = 30
    daily_ocr_quota: int = 500

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
