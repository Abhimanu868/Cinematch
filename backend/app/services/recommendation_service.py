"""Recommendation orchestration service."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ml.trainer import get_content_model, get_hybrid_model
from app.models.movie import Movie
from app.models.rating import Rating
from app.services.movie_service import get_trending_movies

logger = logging.getLogger(__name__)


def get_personal_recommendations(
    db: Session, user_id: int, top_n: int = 20
) -> list[dict]:
    """Get personalized recommendations for an authenticated user.

    Falls back to popularity-based if models can't produce results.
    """
    # Get user's rated movies
    user_ratings = (
        db.query(Rating).filter(Rating.user_id == user_id).all()
    )

    liked_movie_ids = [r.movie_id for r in user_ratings if r.score >= 3.5]
    all_rated_ids = {r.movie_id for r in user_ratings}

    # Try hybrid recommendations
    hybrid = get_hybrid_model()
    recs = hybrid.get_recommendations(
        user_id=user_id,
        liked_movie_ids=liked_movie_ids,
        top_n=top_n,
        exclude_ids=all_rated_ids,
    )

    if recs:
        return _enrich_recommendations(db, recs)

    # Fallback: popularity-based
    logger.info(f"Falling back to popularity-based for user {user_id}")
    popular = get_trending_movies(db, limit=top_n)
    return [
        {
            "movie_id": m.id,
            "score": m.vote_average / 5.0,  # Normalize to 0-1
            "method": "popular",
            "movie": _movie_to_dict(m),
        }
        for m in popular
        if m.id not in all_rated_ids
    ][:top_n]


def get_similar_movies(
    db: Session, movie_id: int, top_n: int = 12
) -> list[dict]:
    """Get movies similar to a given movie (content-based)."""
    content_model = get_content_model()

    if not content_model.is_fitted:
        # Fallback: same genre movies
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie or not movie.genres:
            return []
        first_genre = movie.genres.split(",")[0].strip()
        similar = (
            db.query(Movie)
            .filter(Movie.genres.contains(first_genre), Movie.id != movie_id)
            .order_by(Movie.vote_average.desc())
            .limit(top_n)
            .all()
        )
        return [
            {
                "movie_id": m.id,
                "score": 0.5,
                "method": "genre_fallback",
                "movie": _movie_to_dict(m),
            }
            for m in similar
        ]

    recs = content_model.get_similar_movies(movie_id, top_n)
    return _enrich_recommendations(
        db, [{"movie_id": mid, "score": score, "method": "content"} for mid, score in recs]
    )


def get_popular_movies(db: Session, top_n: int = 20) -> list[dict]:
    """Get globally popular movie picks."""
    movies = get_trending_movies(db, limit=top_n)
    return [
        {
            "movie_id": m.id,
            "score": m.vote_average / 5.0,
            "method": "popular",
            "movie": _movie_to_dict(m),
        }
        for m in movies
    ]


def _enrich_recommendations(db: Session, recs: list[dict]) -> list[dict]:
    """Add full movie data to recommendation results."""
    movie_ids = [r["movie_id"] for r in recs]
    movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
    movie_map = {m.id: m for m in movies}

    enriched = []
    for rec in recs:
        movie = movie_map.get(rec["movie_id"])
        if movie:
            rec["movie"] = _movie_to_dict(movie)
            enriched.append(rec)
    return enriched


def _movie_to_dict(movie: Movie) -> dict:
    """Convert Movie ORM object to a serializable dict."""
    return {
        "id": movie.id,
        "title": movie.title,
        "overview": movie.overview,
        "genres": movie.genres,
        "release_year": movie.release_year,
        "director": movie.director,
        "cast": movie.cast,
        "poster_url": movie.poster_url,
        "backdrop_url": movie.backdrop_url,
        "vote_average": movie.vote_average,
        "vote_count": movie.vote_count,
        "popularity": movie.popularity,
        "runtime": movie.runtime,
    }
