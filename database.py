import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self._client = AsyncIOMotorClient(MONGO_URI)
        self.db = self._client[DB_NAME]
        self.users = self.db.users
        self.search_history = self.db.search_history
        self.premium_users = self.db.premium_users
        self.referrals = self.db.referrals
        self.admins = self.db.admins

    async def add_user(self, user_id, username, full_name):
        user = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "is_premium": False,
            "referred_by": None
        }
        await self.users.update_one({"user_id": user_id}, {"$set": user}, upsert=True)

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    async def add_search_query(self, query):
        await self.search_history.update_one(
            {"query": query.lower()},
            {"$inc": {"count": 1}},
            upsert=True
        )

    async def get_most_searched(self, limit=10):
        return await self.search_history.find().sort("count", -1).limit(limit).to_list(length=limit)

    async def is_admin(self, user_id):
        from config import ADMIN_IDS, OWNER_IDS
        if user_id in OWNER_IDS or user_id in ADMIN_IDS:
            return True
        admin = await self.admins.find_one({"user_id": user_id})
        return admin is not None

    async def add_admin(self, user_id):
        await self.admins.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

    async def remove_admin(self, user_id):
        await self.admins.delete_one({"user_id": user_id})

    async def get_stats(self):
        users_count = await self.users.count_documents({})
        premium_count = await self.premium_users.count_documents({})
        return users_count, premium_count

db = Database()
