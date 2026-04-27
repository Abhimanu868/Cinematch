from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    movie_id: int
    score: float = Field(..., ge=1.0, le=5.0)
    review_text: Optional[str] = Field(None, max_length=2000)
    review_title: Optional[str] = Field(None, max_length=150)


class RatingUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=1.0, le=5.0)
    review_text: Optional[str] = Field(None, max_length=2000)
    review_title: Optional[str] = Field(None, max_length=150)


class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    user_id: int
    username: str
    score: float
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    created_at: datetime
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RatingResponse(BaseModel):
    id: int
    movie_id: int
    user_id: int
    score: float
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    created_at: datetime
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MyRatingResponse(BaseModel):
    """Rating with movie info — used on the Profile page."""
    id: int
    movie_id: int
    movie_title: str
    movie_poster_url: Optional[str] = None
    movie_genres: Optional[str] = None
    score: float
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    created_at: datetime
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True
