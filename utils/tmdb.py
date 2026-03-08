import aiohttp
from config import TMDB_API_KEY

class TMDB:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    async def get_details(self, query):
        async with aiohttp.ClientSession() as session:
            # Search for the movie/series
            search_url = f"{self.base_url}/search/multi"
            params = {
                "api_key": self.api_key,
                "query": query,
                "language": "en-US",
                "page": 1,
                "include_adult": "false"
            }
            async with session.get(search_url, params=params) as resp:
                data = await resp.json()
                if not data.get("results"):
                    return None
                
                result = data["results"][0]
                media_type = result.get("media_type", "movie")
                tmdb_id = result["id"]

                # Fetch detailed info
                details_url = f"{self.base_url}/{media_type}/{tmdb_id}"
                params = {"api_key": self.api_key, "language": "en-US"}
                async with session.get(details_url, params=params) as detail_resp:
                    details = await detail_resp.json()
                    
                    if media_type == "movie":
                        return {
                            "type": "movie",
                            "title": details.get("title"),
                            "year": details.get("release_date", "")[:4],
                            "genres": ", ".join([g["name"] for g in details.get("genres", [])]),
                            "rating": details.get("vote_average"),
                            "plot": details.get("overview"),
                            "audio": "English | Hindi" # Placeholder, usually not in TMDB
                        }
                    else: # TV Series
                        return {
                            "type": "series",
                            "title": details.get("name"),
                            "year": details.get("first_air_date", "")[:4],
                            "status": details.get("status"),
                            "episodes": details.get("number_of_episodes"),
                            "rating": details.get("vote_average"),
                            "genres": ", ".join([g["name"] for g in details.get("genres", [])]),
                            "plot": details.get("overview"),
                            "audio": "English | Hindi" # Placeholder
                        }

tmdb = TMDB(TMDB_API_KEY)
