"""Movie ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Movie(Base):
    """Movie entity with metadata for recommendations."""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    overview = Column(Text, nullable=True)
    genres = Column(String(255), nullable=True)  # Comma-separated genre names
    release_year = Column(Integer, nullable=True)
    director = Column(String(100), nullable=True)
    cast = Column(Text, nullable=True)  # Comma-separated actor names
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    poster_url = Column(String(500), nullable=True)
    backdrop_url = Column(String(500), nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    tagline = Column(String(500), nullable=True)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)
    runtime = Column(Integer, nullable=True)  # In minutes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")

    @property
    def average_rating(self) -> float:
        """Calculate average rating from user ratings."""
        if not self.ratings:
            return 0.0
        return sum(r.score for r in self.ratings) / len(self.ratings)

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, title='{self.title}')>"
