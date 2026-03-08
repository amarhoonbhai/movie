import motor.motor_asyncio
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.requests = self.db.requests
        self.trending = self.db.trending

    async def add_user(self, user_id, first_name, last_name=None):
        user = await self.users.find_one({"_id": user_id})
        user_data = {"_id": user_id, "first_name": first_name, "last_name": last_name}
        if not user:
            return await self.users.insert_one(user_data)
        else:
            # Update names if they changed
            await self.users.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "last_name": last_name}})
        return False

    async def get_all_users(self):
        return await self.users.find({}).to_list(length=None)

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def add_request(self, movie_name, user_id):
        await self.requests.update_one(
            {"name": movie_name.lower()},
            {"$addToSet": {"requested_by": user_id}, "$setOnInsert": {"status": "pending"}},
            upsert=True
        )

    async def get_requests_count(self):
        return await self.requests.count_documents({})

    async def add_trending(self, movie_name):
        await self.trending.update_one(
            {"name": movie_name.lower()},
            {"$inc": {"count": 1}},
            upsert=True
        )

    async def get_trending(self, limit=10):
        return await self.trending.find({}).sort("count", -1).to_list(length=limit)

db = Database(MONGO_URI, DB_NAME)
