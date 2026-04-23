from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingUpdate, RatingResponse, ReviewResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit or update a rating and optional review for a movie."""
    # Check movie exists
    from app.models.movie import Movie
    movie = db.query(Movie).filter(Movie.id == data.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Check for existing rating
    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == data.movie_id
    ).first()
    
    if existing:
        # Update existing
        existing.score = data.score
        if data.review_text is not None:
            existing.review_text = data.review_text
        if data.review_title is not None:
            existing.review_title = data.review_title
        existing.edited_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        rating = Rating(
            user_id=current_user.id,
            movie_id=data.movie_id,
            score=data.score,
            review_text=data.review_text,
            review_title=data.review_title,
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating


@router.get("/movie/{movie_id}", response_model=list[ReviewResponse])
def get_movie_reviews(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific movie, newest first."""
    from app.models.user import User as UserModel
    
    results = (
        db.query(Rating, UserModel.username)
        .join(UserModel, Rating.user_id == UserModel.id)
        .filter(
            Rating.movie_id == movie_id,
            Rating.review_text.isnot(None),
            Rating.review_text != "",
        )
        .order_by(Rating.created_at.desc())
        .all()
    )
    
    reviews = []
    for rating, username in results:
        reviews.append(ReviewResponse(
            id=rating.id,
            movie_id=rating.movie_id,
            user_id=rating.user_id,
            username=username,
            score=rating.score,
            review_text=rating.review_text,
            review_title=rating.review_title,
            created_at=rating.created_at,
            edited_at=rating.edited_at,
        ))
    return reviews


@router.patch("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    data: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edit an existing rating or review. Only the owner can edit."""
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your rating")
    
    if data.score is not None:
        rating.score = data.score
    if data.review_text is not None:
        rating.review_text = data.review_text
    if data.review_title is not None:
        rating.review_title = data.review_title
    rating.edited_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rating)
    return rating


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a rating and its review. Only the owner can delete."""
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your rating")
    
    db.delete(rating)
    db.commit()
