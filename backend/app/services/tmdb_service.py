import os
import httpx
from typing import Optional

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"

async def search_movie_tmdb(title: str, year: Optional[int] = None) -> Optional[dict]:
    """Search TMDB for a movie by title and optional year. Returns first result."""
    if not TMDB_API_KEY:
        return None

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
    }
    if year:
        params["primary_release_year"] = year

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    return data["results"][0]
        except Exception as e:
            print(f"Error searching TMDB for {title}: {e}")
            
    return None

async def get_poster_url(title: str, year: Optional[int] = None) -> Optional[str]:
    """Returns full poster URL for a movie. Returns None if not found."""
    movie = await search_movie_tmdb(title, year)
    if movie and movie.get("poster_path"):
        return f"{TMDB_IMAGE_BASE}{movie['poster_path']}"
    return None

async def get_movie_details(tmdb_id: int) -> Optional[dict]:
    """Get detailed movie info from TMDB using ID (to get tagline)."""
    if not TMDB_API_KEY:
        return None
        
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching TMDB details for {tmdb_id}: {e}")
            
    return None

async def enrich_movie_with_tmdb(movie_title: str, year: Optional[int] = None) -> dict:
    """Returns dict with: poster_url, backdrop_url, tmdb_id, overview, tagline"""
    result = {
        "poster_url": None,
        "backdrop_url": None,
        "tmdb_id": None,
        "overview": None,
        "tagline": None
    }
    
    movie = await search_movie_tmdb(movie_title, year)
    if movie:
        result["tmdb_id"] = movie.get("id")
        result["overview"] = movie.get("overview")
        
        if movie.get("poster_path"):
            result["poster_url"] = f"{TMDB_IMAGE_BASE}{movie['poster_path']}"
            
        if movie.get("backdrop_path"):
            result["backdrop_url"] = f"{TMDB_BACKDROP_BASE}{movie['backdrop_path']}"
            
        # If we found a movie, fetch details for tagline
        if result["tmdb_id"]:
            details = await get_movie_details(result["tmdb_id"])
            if details:
                result["tagline"] = details.get("tagline")
                
    return result
