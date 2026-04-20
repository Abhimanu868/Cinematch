"""Pydantic schemas for Movie endpoints."""

from datetime import datetime
from pydantic import BaseModel, Field


class MovieBase(BaseModel):
    """Shared movie fields."""
    title: str = Field(..., max_length=255)
    overview: str | None = None
    genres: str | None = None
    release_year: int | None = None
    director: str | None = None
    cast: str | None = None
    keywords: str | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    tmdb_id: int | None = None
    tagline: str | None = None
    runtime: int | None = None


class MovieCreate(MovieBase):
    """Schema for creating a movie."""
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0


class MovieResponse(MovieBase):
    """Schema for movie API responses."""
    id: int
    vote_average: float
    vote_count: int
    popularity: float
    average_user_rating: float | None = None
    user_rating: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    """Paginated movie list response."""
    movies: list[MovieResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class MovieSearchResponse(BaseModel):
    """Search results response."""
    movies: list[MovieResponse]
    query: str
    total: int
