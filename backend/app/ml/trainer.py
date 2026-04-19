"""Model training pipeline: train, save, and load ML models."""

import logging
import os
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.ml.collaborative import CollaborativeRecommender
from app.ml.content_based import ContentBasedRecommender
from app.ml.hybrid import HybridRecommender
from app.models.movie import Movie
from app.models.rating import Rating

logger = logging.getLogger(__name__)

# Singleton instances
_content_model: ContentBasedRecommender | None = None
_collaborative_model: CollaborativeRecommender | None = None
_hybrid_model: HybridRecommender | None = None


def get_content_model() -> ContentBasedRecommender:
    global _content_model
    if _content_model is None:
        _content_model = ContentBasedRecommender()
    return _content_model


def get_collaborative_model() -> CollaborativeRecommender:
    global _collaborative_model
    if _collaborative_model is None:
        _collaborative_model = CollaborativeRecommender()
    return _collaborative_model


def get_hybrid_model() -> HybridRecommender:
    global _hybrid_model
    if _hybrid_model is None:
        _hybrid_model = HybridRecommender(
            content_recommender=get_content_model(),
            collaborative_recommender=get_collaborative_model(),
            collaborative_weight=settings.COLLABORATIVE_WEIGHT,
            content_weight=settings.CONTENT_WEIGHT,
        )
    return _hybrid_model


def _get_movies_df(db: Session) -> pd.DataFrame:
    """Load all movies into a pandas DataFrame."""
    movies = db.query(Movie).all()
    if not movies:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "id": m.id,
                "title": m.title,
                "overview": m.overview,
                "genres": m.genres,
                "cast": m.cast,
                "director": m.director,
                "keywords": m.keywords,
                "vote_average": m.vote_average,
                "popularity": m.popularity,
            }
            for m in movies
        ]
    )


def _get_ratings_df(db: Session) -> pd.DataFrame:
    """Load all ratings into a pandas DataFrame."""
    ratings = db.query(Rating).all()
    if not ratings:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "user_id": r.user_id,
                "movie_id": r.movie_id,
                "score": r.score,
            }
            for r in ratings
        ]
    )


def train_models(db: Session) -> dict:
    """Train all ML models from current database data."""
    logger.info("Starting model training pipeline...")

    movies_df = _get_movies_df(db)
    ratings_df = _get_ratings_df(db)

    results = {"content_based": False, "collaborative": False}

    # Train content-based model
    content_model = get_content_model()
    if not movies_df.empty:
        content_model.fit(movies_df)
        results["content_based"] = True
        _save_model(content_model, "content_model.pkl")
        logger.info("Content-based model trained and saved.")
    else:
        logger.warning("No movies found; skipping content-based training.")

    # Train collaborative model
    collab_model = get_collaborative_model()
    if not ratings_df.empty and len(ratings_df) >= 10:
        collab_model.fit(ratings_df)
        results["collaborative"] = True
        _save_model(collab_model, "collaborative_model.pkl")
        logger.info("Collaborative model trained and saved.")
    else:
        logger.warning("Not enough ratings; skipping collaborative training.")

    # Re-initialize hybrid model with fresh sub-models
    global _hybrid_model
    _hybrid_model = HybridRecommender(
        content_recommender=content_model,
        collaborative_recommender=collab_model,
        collaborative_weight=settings.COLLABORATIVE_WEIGHT,
        content_weight=settings.CONTENT_WEIGHT,
    )

    logger.info(f"Training complete: {results}")
    return results


def load_models() -> bool:
    """Load saved models from disk. Returns True if any model loaded."""
    loaded = False

    content_path = _model_path("content_model.pkl")
    if content_path.exists():
        global _content_model
        _content_model = joblib.load(content_path)
        loaded = True
        logger.info("Loaded content-based model from disk.")

    collab_path = _model_path("collaborative_model.pkl")
    if collab_path.exists():
        global _collaborative_model
        _collaborative_model = joblib.load(collab_path)
        loaded = True
        logger.info("Loaded collaborative model from disk.")

    if loaded:
        global _hybrid_model
        _hybrid_model = HybridRecommender(
            content_recommender=get_content_model(),
            collaborative_recommender=get_collaborative_model(),
            collaborative_weight=settings.COLLABORATIVE_WEIGHT,
            content_weight=settings.CONTENT_WEIGHT,
        )

    return loaded


def _save_model(model: object, filename: str) -> None:
    """Save a model to disk using joblib."""
    path = _model_path(filename)
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")


def _model_path(filename: str) -> Path:
    """Get the full path for a model file."""
    return Path(settings.ML_MODELS_DIR) / filename
