"""Poster fetching service using OMDB API with hardcoded TMDB fallbacks."""
import os
import logging

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Hardcoded TMDB poster paths for the 50 curated movies
# Format: "Movie Title (Year)": ("poster_path", "backdrop_path", tmdb_id)
HARDCODED_POSTERS = {
    "The Shawshank Redemption": ("/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg", 278),
    "The Godfather": ("/3bhkrj58Vtu7enYsLegHnDmni69.jpg", "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg", 238),
    "The Dark Knight": ("/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "/hkBaDkMWbLaf8B1lsWsKX7Ew3Xq.jpg", 155),
    "Pulp Fiction": ("/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg", 680),
    "Forrest Gump": ("/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "/7c9UVPPiTPltouxRVY6N9uugaVA.jpg", 13),
    "Inception": ("/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg", 27205),
    "Fight Club": ("/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "/52AfXWuXCHn3UjD17rBruA9f5qb.jpg", 550),
    "The Matrix": ("/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg", 603),
    "Goodfellas": ("/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg", "/sw7mordbZxgITU877yTpZCud90M.jpg", 769),
    "The Lord of the Rings: The Return of the King": ("/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg", "/lXhgCODAbBXL5buk9yEmTpOoOgR.jpg", 122),
    "Interstellar": ("/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "/AbUM2nC2Pzo5cWgOXRnDmfwTgBa.jpg", 157336),
    "The Silence of the Lambs": ("/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg", "/mfwq2nMBzArzQ7Y9RKE8SKeeTkg.jpg", 274),
    "Schindler's List": ("/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", "/loRmRzQXZeqG78TqZuyvSlEQfZb.jpg", 424),
    "The Green Mile": ("/velWPhVMQeQKcxggNEU8YmU1pGt.jpg", "/l6hQWH9eDksNJNiXWYRkWqikOdu.jpg", 497),
    "Se7en": ("/6yoghtyTpznpBik8EngEmJskVnS.jpg", "/xJHokMbljvjADYdit5fK5VQsXEG.jpg", 807),
    "Gladiator": ("/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg", "/5XPPB44RQGFkBUHOCBPXlkFEQCG.jpg", 98),
    "The Departed": ("/nT97ifVT2J1yMQmeq20Qblg61T.jpg", "/8Op7EVHAhlSXszAFbAHOHGMhPMd.jpg", 1422),
    "Whiplash": ("/7fn624j5lj3xTme2SgiLCeuedmO.jpg", "/fRGxZuo7jJUWQsVg9PREb98Aclp.jpg", 244786),
    "The Prestige": ("/5MXyQfz8xUP3dIFPTubhTsbFY6N.jpg", "/eDCJBCCeNMi9qmErV1OGlPRmNS0.jpg", 1124),
    "Django Unchained": ("/7oWY8VDWW7thTzWh3OKYRkWAKdN.jpg", "/2oZklIzUbvZXXzIFzv7Hi68BJmb.jpg", 68718),
    "Parasite": ("/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg", 496243),
    "Joker": ("/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg", "/n6bUvigpRFqSwmPp1ZIzTLjTP4j.jpg", 475557),
    "Avengers: Endgame": ("/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg", 299534),
    "Spider-Man: Into the Spider-Verse": ("/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg", "/9zRBXHPMhqQP8BRCGqN8yCBSb6Y.jpg", 324857),
    "The Lion King": ("/sKCr8huGuTR3eCnizmAMgMjGBUS.jpg", "/wXsQvli6tWqja51pYxXNG1LFIGV.jpg", 8587),
    "Back to the Future": ("/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg", "/3o4bfQ2g5aFBNcheT9VUft0nj68.jpg", 105),
    "Alien": ("/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg", "/AmR3JfHACOxFRtWtgFE74BPuimq.jpg", 348),
    "WALL-E": ("/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg", "/jBJcHBwKBIFRGzrHHqmBFNNTYlo.jpg", 10681),
    "The Truman Show": ("/vuza0WqY239yBXOadKlGwJsZJFE.jpg", "/6TEVHJpvUXNIZlHSBQSvB9pGMjS.jpg", 37165),
    "Spirited Away": ("/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", "/bSFbHkpJzgebBp0BpBxv3f30Ck9.jpg", 129),
    "Coco": ("/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg", "/askg3SMvhqEl4OL52YuvdtY40Yb.jpg", 354912),
    "Mad Max: Fury Road": ("/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg", "/phszHPFnhJCDEFJtpUZn6bHAliN.jpg", 76341),
    "Blade Runner 2049": ("/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg", "/ilRyazdMJwN05exqhwK4tMKBYZs.jpg", 335984),
    "Get Out": ("/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg", "/The4G5C4MRxSqGHCnHBjvjPM5Ye.jpg", 419430),
    "La La Land": ("/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg", "/nadTlnTE6DdgmFCkFAhqBSqpMkD.jpg", 313369),
    "The Grand Budapest Hotel": ("/eWdyYQreja6JiT2n2nQCyFCqEAG.jpg", "/fydpHcDNLMoMaqF5M6kDfXCFDMQ.jpg", 120467),
    "Arrival": ("/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg", "/eIi3klFf7mp3oL5EEF4mLIDs26r.jpg", 329865),
    "Jaws": ("/lxM6e0GFdFxabHJmfSKS4xbqMKY.jpg", "/AvHiXSJe3NTBF3HfRMIFyOrEBQe.jpg", 578),
    "Jurassic Park": ("/oU7Oq2kFAAlGqbU4VoAE36g4hoI.jpg", "/9BBTo108Cly0r0eLLnXeEXEMO3M.jpg", 329),
    "Titanic": ("/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg", "/kHXEpyfl6zqn8a6YuozZUuj2bc8.jpg", 597),
    "The Social Network": ("/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg", "/5WJnfxJFCIUHATEMIRQQfYBiuFN.jpg", 37799),
    "No Country for Old Men": ("/6d5XOczc2iFGKFp9UE0xSLIYh3v.jpg", "/8b0qHnZ9FGY4ylU7IWKxkxQxn5K.jpg", 6966),
    "There Will Be Blood": ("/fa0RDkAlCec0STeMNAhPaF89q6V.jpg", "/kS7NhJSNjNwgm0SLRP28gIGKMnM.jpg", 7345),
    "Eternal Sunshine of the Spotless Mind": ("/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg", "/u6oQdMPcEJhx0RXdCYlAVDqxL9S.jpg", 38),
    "The Big Lebowski": ("/aEpvSqLRNFE46oKX4g5DHJPQ1ip.jpg", "/2XtHhSBCGCxcBsZwXJj3SaSPnVv.jpg", 115),
    "Toy Story": ("/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg", "/mLnRNalMJxHKRCOdqijb7UtHZPO.jpg", 862),
    "Up": ("/pyCJBXXVMBsEkdQXGBCtmDPJsTF.jpg", "/nGJpCdMPRxK0jXeADblNEqDPflg.jpg", 14160),
    "Finding Nemo": ("/eHuGQ10FUzK1p2sD3MW6hADf7a8.jpg", "/78iBIlAlPyBpFGkCgEkBOHSBYuP.jpg", 12),
    "Inside Out": ("/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg", "/oY3pyQILPbMptqXKLrUvxEbmL21.jpg", 150540),
    "Ratatouille": ("/npHNjldbeTHdKKw28bJKs7lzqzj.jpg", "/dIWwZW7dJJtqC6CgWzYkNVKIUm8.jpg", 2062),
}


def fetch_tmdb_poster_sync(title: str, year: int = None) -> dict:
    """
    Fetch poster using 3-tier strategy:
    1. OMDB API (if OMDB_API_KEY set)
    2. Hardcoded TMDB poster paths (for curated movies)
    3. Styled placeholder fallback
    """
    # Tier 1: Try OMDB API
    if OMDB_API_KEY:
        result = _fetch_from_omdb(title, year)
        if result.get("poster_url"):
            return result

    # Tier 2: Try hardcoded TMDB posters
    hardcoded = HARDCODED_POSTERS.get(title)
    if hardcoded:
        poster_path, backdrop_path, tmdb_id = hardcoded
        return {
            "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}",
            "backdrop_url": f"{TMDB_BACKDROP_BASE}{backdrop_path}",
            "tmdb_id": tmdb_id,
            "overview": "",
        }

    # Tier 3: Styled placeholder (much better than plain placehold.co)
    return {}


def _fetch_from_omdb(title: str, year: int = None) -> dict:
    """Fetch poster from OMDB API."""
    try:
        import httpx
        params = {"apikey": OMDB_API_KEY, "t": title, "type": "movie"}
        if year:
            params["y"] = year

        with httpx.Client(timeout=8.0) as client:
            r = client.get(OMDB_BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()

        if data.get("Response") == "True" and data.get("Poster") not in (None, "N/A", ""):
            poster_url = data["Poster"]
            # Upgrade to higher resolution
            poster_url = poster_url.replace("SX300", "SX600")
            return {
                "poster_url": poster_url,
                "backdrop_url": None,
                "tmdb_id": None,
                "overview": data.get("Plot", ""),
            }
        return {}
    except Exception as e:
        logger.warning(f"OMDB fetch failed for '{title}': {e}")
        return {}


async def fetch_tmdb_poster(title: str, year: int = None) -> dict:
    """Async version — delegates to sync for simplicity."""
    return fetch_tmdb_poster_sync(title, year)
