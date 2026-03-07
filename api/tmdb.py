import logging
import httpx
from config import TMDB_API_KEY

logger = logging.getLogger(__name__)

TMDB_BASE = "https://api.themoviedb.org/3"


class TMDB:
    def __init__(self):
        self._api_key = TMDB_API_KEY

    async def _get(self, path, params=None):
        """Central GET with error handling."""
        _params = {"api_key": self._api_key, "language": "en-US"}
        if params:
            _params.update(params)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{TMDB_BASE}{path}", params=_params)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"TMDb HTTP error: {e.response.status_code} for {path}")
            return {}
        except Exception as e:
            logger.error(f"TMDb request failed: {e}")
            return {}

    async def search(self, query):
        data = await self._get("/search/multi", {"query": query, "page": 1, "include_adult": False})
        results = data.get("results", [])
        return [r for r in results if r.get("media_type") in ("movie", "tv")][:5]

    async def get_details(self, media_type, media_id):
        return await self._get(f"/{media_type}/{media_id}")

    async def get_trending(self, media_type="all", time_window="day"):
        data = await self._get(f"/trending/{media_type}/{time_window}")
        return data.get("results", [])[:10]


tmdb = TMDB()
