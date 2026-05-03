import asyncio
from backend.utils.db import connect_to_mongo, get_db

async def test():
    await connect_to_mongo()
    db = get_db()
    print("DB:", db)
    user = await db.users.find_one({"email": "test"})
    print("User:", user)

asyncio.run(test())
