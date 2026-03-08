"""
utils/tmdb.py — TMDb API client (async, aiohttp).
"""
import logging
import aiohttp
from config import TMDB_API_KEY, TMDB_IMAGE_BASE

logger = logging.getLogger(__name__)

BASE_URL = "https://api.themoviedb.org/3"


class TMDb:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _params(self, extra: dict = None) -> dict:
        p = {"api_key": self.api_key, "language": "en-US"}
        if extra:
            p.update(extra)
        return p

    async def search(self, query: str, page: int = 1) -> list:
        """Multi-search: returns list of raw results (movie + tv)."""
        url = f"{BASE_URL}/search/multi"
        params = self._params({"query": query, "page": page, "include_adult": "false"})
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    return [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
        except Exception as e:
            logger.error(f"TMDb search error: {e}")
            return []

    async def get_details(self, media_type: str, tmdb_id) -> dict:
        """Fetch full details for a movie or TV show."""
        url = f"{BASE_URL}/{media_type}/{tmdb_id}"
        params = self._params()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"TMDb get_details error: {e}")
            return {}

    async def get_movie_info(self, query: str) -> dict | None:
        """
        Single-call convenience method.
        Returns a unified dict ready for caption formatting, or None.
        """
        results = await self.search(query)
        if not results:
            return None

        best = results[0]
        media_type = best.get("media_type", "movie")
        tmdb_id    = best.get("id")
        details    = await self.get_details(media_type, tmdb_id)
        if not details:
            return None

        genres = ", ".join(g["name"] for g in details.get("genres", []))
        rating = details.get("vote_average", 0)
        poster = details.get("poster_path")

        if media_type == "movie":
            return {
                "type":        "movie",
                "title":       details.get("title") or best.get("title") or query,
                "year":        (details.get("release_date") or "")[:4] or "N/A",
                "genres":      genres or "N/A",
                "rating":      f"{rating:.1f} ⭐" if rating else "N/A",
                "plot":        details.get("overview") or "No description available.",
                "poster_url":  f"{TMDB_IMAGE_BASE}{poster}" if poster else None,
                "media_type":  "movie",
            }
        else:
            return {
                "type":        "series",
                "title":       details.get("name") or best.get("name") or query,
                "year":        (details.get("first_air_date") or "")[:4] or "N/A",
                "status":      details.get("status") or "N/A",
                "episodes":    details.get("number_of_episodes") or "N/A",
                "genres":      genres or "N/A",
                "rating":      f"{rating:.1f} ⭐" if rating else "N/A",
                "plot":        details.get("overview") or "No description available.",
                "poster_url":  f"{TMDB_IMAGE_BASE}{poster}" if poster else None,
                "media_type":  "tv",
            }


tmdb = TMDb(TMDB_API_KEY)
