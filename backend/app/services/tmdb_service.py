"""TMDB API service for fetching real movie poster images."""
import os
import time
import logging

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"


def fetch_tmdb_poster_sync(title: str, year: int = None) -> dict:
    """
    Fetch poster data from TMDB synchronously.
    Returns dict with poster_url, backdrop_url, tmdb_id, overview.
    Returns empty dict safely if API key is missing or any error occurs.
    """
    if not TMDB_API_KEY:
        logger.debug(f"TMDB_API_KEY not set, skipping fetch for: {title}")
        return {}

    try:
        import httpx
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US",
            "page": 1,
        }
        if year:
            params["year"] = year

        with httpx.Client(timeout=8.0) as client:
            response = client.get(TMDB_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if not results:
            return {}

        movie = results[0]
        poster_path = movie.get("poster_path")
        backdrop_path = movie.get("backdrop_path")

        return {
            "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None,
            "backdrop_url": f"{TMDB_BACKDROP_BASE}{backdrop_path}" if backdrop_path else None,
            "tmdb_id": movie.get("id"),
            "overview": movie.get("overview") or "",
        }

    except Exception as e:
        logger.warning(f"TMDB fetch failed for '{title}': {e}")
        return {}


async def fetch_tmdb_poster(title: str, year: int = None) -> dict:
    """Async version for use in FastAPI endpoints."""
    if not TMDB_API_KEY:
        return {}

    try:
        import httpx
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US",
            "page": 1,
        }
        if year:
            params["year"] = year

        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(TMDB_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if not results:
            return {}

        movie = results[0]
        poster_path = movie.get("poster_path")
        backdrop_path = movie.get("backdrop_path")

        return {
            "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None,
            "backdrop_url": f"{TMDB_BACKDROP_BASE}{backdrop_path}" if backdrop_path else None,
            "tmdb_id": movie.get("id"),
            "overview": movie.get("overview") or "",
        }

    except Exception as e:
        logger.warning(f"TMDB async fetch failed for '{title}': {e}")
        return {}
