"""Movie business logic service."""

import math
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.rating import Rating


def get_movies(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    genre: Optional[str] = None,
    sort_by: str = "popularity",
) -> tuple[list[Movie], int]:
    """Get paginated movie list with optional genre filter."""
    query = db.query(Movie)

    if genre:
        query = query.filter(Movie.genres.contains(genre))

    # Sorting
    if sort_by == "rating":
        query = query.order_by(Movie.vote_average.desc())
    elif sort_by == "year":
        query = query.order_by(Movie.release_year.desc())
    elif sort_by == "title":
        query = query.order_by(Movie.title.asc())
    else:
        query = query.order_by(Movie.popularity.desc())

    total = query.count()
    movies = query.offset((page - 1) * per_page).limit(per_page).all()
    return movies, total


def search_movies(db: Session, query_str: str, limit: int = 20) -> list[Movie]:
    """Full-text search movies by title, overview, genres, cast."""
    search = f"%{query_str}%"
    return (
        db.query(Movie)
        .filter(
            or_(
                Movie.title.ilike(search),
                Movie.overview.ilike(search),
                Movie.genres.ilike(search),
                Movie.cast.ilike(search),
                Movie.director.ilike(search),
                Movie.keywords.ilike(search),
            )
        )
        .order_by(Movie.popularity.desc())
        .limit(limit)
        .all()
    )


def get_trending_movies(db: Session, limit: int = 20) -> list[Movie]:
    """Get top-rated movies with minimum vote count for quality."""
    return (
        db.query(Movie)
        .filter(Movie.vote_count >= 10)
        .order_by(Movie.vote_average.desc(), Movie.popularity.desc())
        .limit(limit)
        .all()
    )


def get_movie_by_id(db: Session, movie_id: int) -> Optional[Movie]:
    """Get a single movie by ID."""
    return db.query(Movie).filter(Movie.id == movie_id).first()


def get_movie_user_rating(
    db: Session, movie_id: int, user_id: int
) -> Optional[float]:
    """Get the current user's rating for a specific movie."""
    rating = (
        db.query(Rating)
        .filter(Rating.movie_id == movie_id, Rating.user_id == user_id)
        .first()
    )
    return rating.score if rating else None


def get_all_genres(db: Session) -> list[str]:
    """Extract all unique genres from the database."""
    movies = db.query(Movie.genres).filter(Movie.genres.isnot(None)).all()
    genres = set()
    for (genre_str,) in movies:
        if genre_str:
            for g in genre_str.split(","):
                g = g.strip()
                if g:
                    genres.add(g)
    return sorted(genres)
