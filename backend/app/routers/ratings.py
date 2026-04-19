"""Rating routes: create, update, list user ratings."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingListResponse, RatingResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RatingResponse:
    """Submit or update a movie rating (1-5 stars)."""
    # Verify movie exists
    movie = db.query(Movie).filter(Movie.id == rating_data.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Check for existing rating (upsert)
    existing = (
        db.query(Rating)
        .filter(
            Rating.user_id == current_user.id,
            Rating.movie_id == rating_data.movie_id,
        )
        .first()
    )

    if existing:
        existing.score = rating_data.score
        db.commit()
        db.refresh(existing)
        rating = existing
    else:
        rating = Rating(
            user_id=current_user.id,
            movie_id=rating_data.movie_id,
            score=rating_data.score,
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)

    return RatingResponse(
        id=rating.id,
        user_id=rating.user_id,
        movie_id=rating.movie_id,
        score=rating.score,
        movie_title=movie.title,
        movie_poster_url=movie.poster_url,
        created_at=rating.created_at,
        updated_at=rating.updated_at,
    )


@router.get("/my-ratings", response_model=RatingListResponse)
def get_my_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RatingListResponse:
    """Get all ratings by the current user."""
    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == current_user.id)
        .order_by(Rating.updated_at.desc())
        .all()
    )

    rating_responses = []
    for r in ratings:
        movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
        rating_responses.append(
            RatingResponse(
                id=r.id,
                user_id=r.user_id,
                movie_id=r.movie_id,
                score=r.score,
                movie_title=movie.title if movie else None,
                movie_poster_url=movie.poster_url if movie else None,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return RatingListResponse(ratings=rating_responses, total=len(rating_responses))


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a user's rating."""
    rating = (
        db.query(Rating)
        .filter(Rating.id == rating_id, Rating.user_id == current_user.id)
        .first()
    )
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )
    db.delete(rating)
    db.commit()
