import asyncio
from fastapi.testclient import TestClient
from backend.app import app
from backend.utils.db import connect_to_mongo

async def main():
    await connect_to_mongo()
    client = TestClient(app)
    response = client.post(
        "/api/auth/register",
        json={"name": "test", "email": "test@test.com", "password": "pass"}
    )
    print("STATUS:", response.status_code)
    print("BODY:", response.text)

asyncio.run(main())
