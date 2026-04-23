"""Application configuration using Pydantic settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Movie Recommendation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # TMDB API
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "4d6c2b6693e7661b4b1dc0c4277c673a")
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"
    TMDB_BACKDROP_BASE_URL: str = "https://image.tmdb.org/t/p/w1280"

    # Database
    DATABASE_URL: str = "sqlite:///./cinematch.db"

    # JWT Auth
    SECRET_KEY: str = "cinematch_jwt_secret_key_2024_do_not_share"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ML Settings
    ML_MODELS_DIR: str = str(Path(__file__).parent.parent / "ml_models")
    COLLABORATIVE_WEIGHT: float = 0.6
    CONTENT_WEIGHT: float = 0.4
    TOP_N_RECOMMENDATIONS: int = 20
    MIN_RATINGS_FOR_COLLABORATIVE: int = 5

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
        "http://frontend:5173",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Ensure ML models directory exists
os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
