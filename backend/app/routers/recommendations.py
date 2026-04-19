"""Recommendation routes: personal, similar, popular, retrain."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.trainer import train_models
from app.models.user import User
from app.services.auth_service import get_admin_user, get_current_user
from app.services.recommendation_service import (
    get_personal_recommendations,
    get_popular_movies,
    get_similar_movies,
)

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/personal")
def personal_recommendations(
    top_n: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get personalized ML-driven recommendations for the authenticated user."""
    recs = get_personal_recommendations(db, current_user.id, top_n)
    return recs


@router.get("/similar/{movie_id}")
def similar_movies(
    movie_id: int,
    top_n: int = Query(12, ge=1, le=30),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Get movies similar to a given movie (content-based)."""
    from app.services.movie_service import get_movie_by_id

    movie = get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return get_similar_movies(db, movie_id, top_n)


@router.get("/popular")
def popular_movies(
    top_n: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Get globally popular movie picks."""
    return get_popular_movies(db, top_n)


@router.post("/retrain")
def retrain_models(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
) -> dict:
    """Retrain all ML models (admin only)."""
    results = train_models(db)
    return {"message": "Models retrained successfully", "results": results}
