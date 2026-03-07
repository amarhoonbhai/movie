import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        # In-memory storage instead of MongoDB
        self._users = {}           # user_id: user_data
        self._search_history = {}  # query: count
        self._premium_users = []   # list of user_ids
        self._referrals = {}       # user_id: count
        self._admins = set()       # set of user_ids
        self._indexed_files = {}   # caption: message_id
        self._movie_requests = []  # list of movie_names

    # --- User Management ---

    async def add_user(self, user_id, username, full_name):
        self._users[user_id] = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "is_premium": False,
            "is_banned": False,
            "referred_by": None,
        }

    async def get_user(self, user_id):
        return self._users.get(user_id)

    async def ban_user(self, user_id):
        user = self._users.get(int(user_id))
        if user:
            user["is_banned"] = True

    async def get_all_users(self):
        return list(self._users.values())

    async def get_stats(self):
        return len(self._users), len(self._premium_users)

    # --- Search History ---

    async def add_search_query(self, query):
        q = query.lower()
        self._search_history[q] = self._search_history.get(q, 0) + 1

    async def get_most_searched(self, limit=10):
        sorted_history = sorted(
            self._search_history.items(), key=lambda x: x[1], reverse=True
        )
        return [{"query": q, "count": c} for q, c in sorted_history[:limit]]

    # --- Admin Management ---

    async def is_admin(self, user_id):
        from config import ADMIN_IDS, OWNER_IDS

        if user_id in OWNER_IDS or user_id in ADMIN_IDS:
            return True
        return user_id in self._admins

    async def add_admin(self, user_id):
        self._admins.add(int(user_id))

    async def remove_admin(self, user_id):
        self._admins.discard(int(user_id))

    # --- Storage Index ---

    async def index_file(self, caption, message_id):
        if caption:
            self._indexed_files[caption.lower()] = message_id
            logger.info(f"Indexed: {caption[:40]}... -> msg#{message_id}")

    async def search_files(self, query):
        query = query.lower().strip()
        results = []
        for caption, msg_id in self._indexed_files.items():
            if query in caption:
                results.append({"caption": caption, "message_id": msg_id})
        return results

    # --- Movie Requests ---

    async def add_movie_request(self, movie_name):
        self._movie_requests.append(movie_name.lower().strip())

    async def get_movie_requests(self):
        return list(self._movie_requests)


db = Database()
