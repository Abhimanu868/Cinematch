"""Movie CRUD and search routes."""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.movie import MovieListResponse, MovieResponse, MovieSearchResponse
from app.services.auth_service import get_optional_user
from app.services.movie_service import (
    get_all_genres,
    get_movie_by_id,
    get_movie_user_rating,
    get_movies,
    get_trending_movies,
    search_movies,
)

router = APIRouter(prefix="/api/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    genre: Optional[str] = Query(None),
    sort_by: str = Query("popularity"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> MovieListResponse:
    """Get paginated movie listing with optional genre filter."""
    movies, total = get_movies(db, page, per_page, genre, sort_by)
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    movie_responses = []
    for movie in movies:
        user_rating = None
        if current_user:
            user_rating = get_movie_user_rating(db, movie.id, current_user.id)
        movie_responses.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                overview=movie.overview,
                genres=movie.genres,
                release_year=movie.release_year,
                director=movie.director,
                cast=movie.cast,
                keywords=movie.keywords,
                poster_url=movie.poster_url,
                backdrop_url=movie.backdrop_url,
                vote_average=movie.vote_average,
                vote_count=movie.vote_count,
                popularity=movie.popularity,
                runtime=movie.runtime,
                average_user_rating=movie.average_rating,
                user_rating=user_rating,
                created_at=movie.created_at,
            )
        )

    return MovieListResponse(
        movies=movie_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/search", response_model=MovieSearchResponse)
def search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> MovieSearchResponse:
    """Full-text search movies."""
    movies = search_movies(db, q)
    movie_responses = []
    for movie in movies:
        user_rating = None
        if current_user:
            user_rating = get_movie_user_rating(db, movie.id, current_user.id)
        movie_responses.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                overview=movie.overview,
                genres=movie.genres,
                release_year=movie.release_year,
                director=movie.director,
                cast=movie.cast,
                keywords=movie.keywords,
                poster_url=movie.poster_url,
                backdrop_url=movie.backdrop_url,
                vote_average=movie.vote_average,
                vote_count=movie.vote_count,
                popularity=movie.popularity,
                runtime=movie.runtime,
                average_user_rating=movie.average_rating,
                user_rating=user_rating,
                created_at=movie.created_at,
            )
        )
    return MovieSearchResponse(movies=movie_responses, query=q, total=len(movie_responses))


@router.get("/trending", response_model=list[MovieResponse])
def trending(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[MovieResponse]:
    """Get trending/top-rated movies."""
    movies = get_trending_movies(db, limit)
    return [
        MovieResponse(
            id=m.id,
            title=m.title,
            overview=m.overview,
            genres=m.genres,
            release_year=m.release_year,
            director=m.director,
            cast=m.cast,
            keywords=m.keywords,
            poster_url=m.poster_url,
            backdrop_url=m.backdrop_url,
            vote_average=m.vote_average,
            vote_count=m.vote_count,
            popularity=m.popularity,
            runtime=m.runtime,
            created_at=m.created_at,
        )
        for m in movies
    ]


@router.get("/genres", response_model=list[str])
def genres(db: Session = Depends(get_db)) -> list[str]:
    """Get all unique genres."""
    return get_all_genres(db)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> MovieResponse:
    """Get a single movie by ID."""
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    user_rating = None
    if current_user:
        user_rating = get_movie_user_rating(db, movie.id, current_user.id)

    return MovieResponse(
        id=movie.id,
        title=movie.title,
        overview=movie.overview,
        genres=movie.genres,
        release_year=movie.release_year,
        director=movie.director,
        cast=movie.cast,
        keywords=movie.keywords,
        poster_url=movie.poster_url,
        backdrop_url=movie.backdrop_url,
        vote_average=movie.vote_average,
        vote_count=movie.vote_count,
        popularity=movie.popularity,
        runtime=movie.runtime,
        average_user_rating=movie.average_rating,
        user_rating=user_rating,
        created_at=movie.created_at,
    )


@router.post("/admin/fetch-posters")
async def backfill_posters(db: Session = Depends(get_db)):
    from app.services.tmdb_service import fetch_tmdb_poster
    import asyncio, time
    from app.models.movie import Movie
    
    movies = db.query(Movie).all()
    updated, skipped, failed = 0, 0, 0
    
    for movie in movies:
        # Skip if already has a valid TMDB URL
        if movie.poster_url and "image.tmdb.org" in movie.poster_url:
            skipped += 1
            continue
        
        data = await fetch_tmdb_poster(movie.title, getattr(movie, 'release_year', None))
        if data.get("poster_url"):
            movie.poster_url = data["poster_url"]
            movie.backdrop_url = data.get("backdrop_url")
            movie.tmdb_id = data.get("tmdb_id")
            updated += 1
        else:
            movie.poster_url = f"https://placehold.co/300x450/1a1a2e/white?text={movie.title.replace(' ', '+')}"
            failed += 1
        
        await asyncio.sleep(0.25)
    
    db.commit()
    return {"updated": updated, "skipped": skipped, "failed": failed}

