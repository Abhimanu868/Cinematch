import httpx
import os
import asyncio

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"

async def fetch_tmdb_poster(title: str, year: int = None) -> dict:
    """
    Search TMDB for a movie and return poster_url, backdrop_url, tmdb_id.
    Returns empty dict if not found or API key is missing.
    """
    if not TMDB_API_KEY:
        return {}
    
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US",
        "page": 1
    }
    if year:
        params["year"] = year
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
                "overview": movie.get("overview", ""),
            }
    except Exception as e:
        print(f"TMDB fetch error for '{title}': {e}")
        return {}


def fetch_tmdb_poster_sync(title: str, year: int = None) -> dict:
    """Synchronous wrapper for use in seeding scripts."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(fetch_tmdb_poster(title, year))
    except Exception:
        return asyncio.run(fetch_tmdb_poster(title, year))
