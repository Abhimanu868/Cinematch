"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.ml.trainer import load_models, train_models
from app.routers import auth, movies, ratings, recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Loading ML models...")
    if not load_models():
        logger.info("No saved models found. Will train after seeding.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(recommendations.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.post("/api/seed")
def seed_database():
    """Seed the database with movies and ratings, then train models."""
    from app.database import SessionLocal
    from app.utils.seed_data import seed_movies_and_ratings
    db = SessionLocal()
    try:
        result = seed_movies_and_ratings(db)
        train_result = train_models(db)
        return {"seed": result, "training": train_result}
    finally:
        db.close()

