"""
Async MongoDB layer using Motor.
Collections: files, users, requests, search_stats
"""
import logging
from datetime import datetime, timezone
import motor.motor_asyncio
from pymongo import TEXT, ASCENDING, DESCENDING
from config import MONGO_URI, DB_NAME

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, uri: str, db_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db       = self._client[db_name]

        # Collections
        self.files        = self.db["files"]
        self.users        = self.db["users"]
        self.requests     = self.db["requests"]
        self.search_stats = self.db["search_stats"]

    # ──────────────────────────────────────────────────────────────────────────
    # Indexes
    # ──────────────────────────────────────────────────────────────────────────

    async def ensure_indexes(self):
        """Create MongoDB indexes for fast lookups. Safe to call on every start."""
        try:
            # Text index for full-text search on file_name + caption
            await self.files.create_index(
                [("file_name", TEXT), ("caption", TEXT)],
                name="file_text_idx"
            )
            # Unique on message_id to avoid duplicates
            await self.files.create_index(
                [("message_id", ASCENDING)],
                unique=True,
                name="message_id_unique"
            )
            # Users
            await self.users.create_index(
                [("user_id", ASCENDING)], unique=True, name="user_id_unique"
            )
            # Requests
            await self.requests.create_index(
                [("movie", ASCENDING)], name="request_movie_idx"
            )
            # Search stats
            await self.search_stats.create_index(
                [("query", ASCENDING)], unique=True, name="search_query_unique"
            )
            logger.info("✅ MongoDB indexes ensured.")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # Users
    # ──────────────────────────────────────────────────────────────────────────

    async def add_user(self, user_id: int, first_name: str, username: str = None):
        """Insert or update user record."""
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "first_name": first_name,
                    "username": username,
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "joined_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
        )

    async def get_all_users(self):
        return await self.users.find({}, {"user_id": 1}).to_list(length=None)

    async def total_users_count(self) -> int:
        return await self.users.count_documents({})

    # ──────────────────────────────────────────────────────────────────────────
    # File Indexing
    # ──────────────────────────────────────────────────────────────────────────

    async def index_file(
        self,
        file_id: str,
        file_name: str,
        file_size: int,
        message_id: int,
        caption: str = "",
        upload_time: datetime = None,
    ):
        """Upsert a file document. Uses message_id as unique key."""
        if upload_time is None:
            upload_time = datetime.now(timezone.utc)
        try:
            await self.files.update_one(
                {"message_id": message_id},
                {
                    "$set": {
                        "file_id":    file_id,
                        "file_name":  file_name,
                        "file_size":  file_size,
                        "caption":    caption or file_name,
                        "upload_time": upload_time,
                    },
                    "$setOnInsert": {"message_id": message_id},
                },
                upsert=True,
            )
            return True
        except Exception as e:
            logger.error(f"index_file error: {e}")
            return False

    async def search_files(self, query: str, limit: int = 10):
        """Search files using MongoDB text index + regex fallback."""
        results = []
        try:
            # Primary: text search
            cursor = self.files.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            results = await cursor.to_list(length=limit)
        except Exception:
            pass

        # Fallback: regex (case-insensitive) if text search returns nothing
        if not results:
            try:
                import re
                pattern = re.compile(re.escape(query), re.IGNORECASE)
                cursor = self.files.find(
                    {"file_name": {"$regex": pattern}}
                ).limit(limit)
                results = await cursor.to_list(length=limit)
            except Exception as e:
                logger.error(f"search_files regex error: {e}")

        return results

    async def files_count(self) -> int:
        return await self.files.count_documents({})

    # ──────────────────────────────────────────────────────────────────────────
    # Movie Requests
    # ──────────────────────────────────────────────────────────────────────────

    async def add_request(self, user_id: int, movie: str):
        """Add or update a movie request. Prevents duplicate entries per user."""
        movie_lower = movie.lower().strip()
        await self.requests.update_one(
            {"movie": movie_lower},
            {
                "$addToSet": {"requested_by": user_id},
                "$setOnInsert": {
                    "movie": movie_lower,
                    "requested_at": datetime.now(timezone.utc),
                    "status": "pending",
                },
            },
            upsert=True,
        )

    async def get_pending_requests(self, movie: str):
        """Return list of user_ids who requested this movie."""
        movie_lower = movie.lower().strip()
        doc = await self.requests.find_one({"movie": {"$regex": movie_lower, "$options": "i"}})
        if doc:
            return doc.get("requested_by", [])
        return []

    async def get_all_requests(self, limit: int = 20):
        """Return all pending requests sorted by request count (desc)."""
        pipeline = [
            {"$match": {"status": "pending"}},
            {"$addFields": {"count": {"$size": "$requested_by"}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return await self.requests.aggregate(pipeline).to_list(length=limit)

    async def get_requests_count(self) -> int:
        return await self.requests.count_documents({})

    async def mark_request_fulfilled(self, movie: str):
        await self.requests.update_one(
            {"movie": {"$regex": movie.lower(), "$options": "i"}},
            {"$set": {"status": "fulfilled"}},
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Trending / Search Stats
    # ──────────────────────────────────────────────────────────────────────────

    async def add_search_stat(self, query: str):
        """Track a normalized search query."""
        from utils.helpers import normalize_query
        q = normalize_query(query)
        if not q:
            return
        await self.search_stats.update_one(
            {"query": q},
            {
                "$inc": {"count": 1},
                "$setOnInsert": {"query": q},
            },
            upsert=True,
        )

    async def get_trending(self, limit: int = 10):
        return await self.search_stats.find({}).sort("count", DESCENDING).to_list(length=limit)

    # Keep backward-compat alias
    async def add_trending(self, query: str):
        return await self.add_search_stat(query)


db = Database(MONGO_URI, DB_NAME)
