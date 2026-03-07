class Database:
    def __init__(self):
        # In-memory storage instead of MongoDB
        self._users = {}           # user_id: user_data
        self._search_history = {}  # query: count
        self._premium_users = []   # list of user_ids
        self._referrals = {}       # user_id: count
        self._admins = set()       # set of user_ids

    async def add_user(self, user_id, username, full_name):
        user = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "is_premium": False,
            "referred_by": None
        }
        self._users[user_id] = user

    async def get_user(self, user_id):
        return self._users.get(user_id)

    async def add_search_query(self, query):
        q = query.lower()
        self._search_history[q] = self._search_history.get(q, 0) + 1

    async def get_most_searched(self, limit=10):
        # Return list of dicts to match previous format: [{"query": q, "count": c}, ...]
        sorted_history = sorted(self._search_history.items(), key=lambda x: x[1], reverse=True)
        return [{"query": q, "count": c} for q, c in sorted_history[:limit]]

    async def is_admin(self, user_id):
        from config import ADMIN_IDS, OWNER_IDS
        if user_id in OWNER_IDS or user_id in ADMIN_IDS:
            return True
        return user_id in self._admins

    async def add_admin(self, user_id):
        self._admins.add(user_id)

    async def remove_admin(self, user_id):
        self._admins.discard(user_id)

    async def get_stats(self):
        users_count = len(self._users)
        premium_count = len(self._premium_users)
        return users_count, premium_count

db = Database()
