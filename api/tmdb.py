import httpx
from config import TMDB_API_KEY, TMDB_IMAGE_BASE_URL

class TMDB:
    def __init__(self):
        self._api_key = TMDB_API_KEY
        self._base_url = "https://api.themoviedb.org/3"

    async def search(self, query):
        url = f"{self._base_url}/search/multi"
        params = {
            "api_key": self._api_key,
            "query": query,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            # Filter results to include only movies and series
            return [res for res in results if res["media_type"] in ["movie", "tv"]][:5]

    async def get_details(self, media_type, media_id):
        url = f"{self._base_url}/{media_type}/{media_id}"
        params = {
            "api_key": self._api_key,
            "language": "en-US"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_trending(self, media_type="all", time_window="day"):
        url = f"{self._base_url}/trending/{media_type}/{time_window}"
        params = {
            "api_key": self._api_key,
            "language": "en-US"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            return results[:10]

tmdb = TMDB()
