from functools import lru_cache
from pathlib import Path

from pydantic import ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", protected_namespaces=("settings_",))

    app_name: str = "Emotion Detection Chatbot"
    environment: str = "development"
    database_url: str = "sqlite:///./emotion_chatbot.db"
    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    model_dir: str = "model_artifacts/electra-goemotions"
    fallback_inference: bool = True
    tmdb_api_key: str = ""
    lastfm_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_model_dir(self) -> Path:
        return Path(self.model_dir)

    @model_validator(mode="after")
    def reject_default_secret_outside_safe_environments(self):
        safe_environments = {"development", "dev", "test", "testing"}
        if self.environment.lower() not in safe_environments and self.secret_key == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed outside development/test environments.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
