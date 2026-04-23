"""Rating ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint, Text, String
from sqlalchemy.orm import relationship

from app.database import Base


class Rating(Base):
    """User rating for a movie (1.0 - 5.0 scale)."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 1.0 to 5.0
    review_text = Column(Text, nullable=True)        # the written review
    review_title = Column(String(150), nullable=True)  # optional short headline
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)     # set when review is edited

    # Relationships
    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")

    # Unique constraint: one rating per user per movie
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_rating"),
    )

    def __repr__(self) -> str:
        return f"<Rating(user_id={self.user_id}, movie_id={self.movie_id}, score={self.score})>"
