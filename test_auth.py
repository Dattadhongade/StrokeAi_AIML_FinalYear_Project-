import asyncio
from backend.utils.db import connect_to_mongo
from backend.routes.auth import register, UserRegister

async def main():
    await connect_to_mongo()
    user = UserRegister(name="test", email="test2@test.com", password="pass")
    try:
        res = await register(user)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
