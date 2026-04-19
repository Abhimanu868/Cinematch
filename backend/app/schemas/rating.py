"""Pydantic schemas for Rating endpoints."""

from datetime import datetime
from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    """Shared rating fields."""
    movie_id: int
    score: float = Field(..., ge=1.0, le=5.0)


class RatingCreate(RatingBase):
    """Schema for creating/updating a rating."""
    pass


class RatingResponse(RatingBase):
    """Schema for rating API responses."""
    id: int
    user_id: int
    movie_title: str | None = None
    movie_poster_url: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RatingListResponse(BaseModel):
    """List of user ratings."""
    ratings: list[RatingResponse]
    total: int
