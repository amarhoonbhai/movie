import logging
from meilisearch_python_async import Client
from core.config import MEILI_URL, MEILI_MASTER_KEY

logger = logging.getLogger(__name__)

class MeiliSearchClient:
    def __init__(self, url: str, master_key: str):
        self._client = Client(url, master_key)
        self.index_name = "movies"

    async def ensure_index(self):
        """Creates the index and sets up searchable/filterable attributes."""
        try:
            # Create index if it doesn't exist
            # meilisearch-python-async handles index creation easily usually
            index = self._client.index(self.index_name)
            
            # Setup settings
            await index.update_searchable_attributes([
                "title",
                "year",
                "genre",
                "caption"
            ])
            await index.update_filterable_attributes([
                "year",
                "genre"
            ])
            logger.info("✅ Meilisearch index ensured.")
        except Exception as e:
            logger.warning(f"Meilisearch index creation warning: {e}")

    async def index_movie(self, movie_id: str, title: str, year: str, genre: str, caption: str):
        """Indexes a movie document."""
        index = self._client.index(self.index_name)
        doc = {
            "id": movie_id,  # Meilisearch requires an 'id' field
            "title": title,
            "year": year,
            "genre": genre,
            "caption": caption
        }
        try:
            await index.add_documents([doc])
            return True
        except Exception as e:
            logger.error(f"Failed to index movie in Meilisearch: {e}")
            return False

    async def search_movies(self, query: str, limit: int = 10):
        """Fuzzy search for movies."""
        index = self._client.index(self.index_name)
        try:
            results = await index.search(query, limit=limit)
            return results.hits
        except Exception as e:
            logger.error(f"Failed to search Meilisearch: {e}")
            return []

meili = MeiliSearchClient(MEILI_URL, MEILI_MASTER_KEY)
