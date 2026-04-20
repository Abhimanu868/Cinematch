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
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"
    TMDB_BACKDROP_BASE_URL: str = "https://image.tmdb.org/t/p/w1280"

    # Database
    DATABASE_URL: str = "sqlite:///./movie_recommender.db"

    # JWT Auth
    SECRET_KEY: str = "super-secret-key-change-in-production"
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
        "http://localhost:3000",
        "http://frontend:5173",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Ensure ML models directory exists
os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
