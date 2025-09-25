#!/usr/bin/env python3
"""
Check user fields in detail
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_user_fields():
    # MongoDB connection
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["emergent"]
    
    print("🔍 Checking all users for 'id' field...")
    users_with_id = await db.users.count_documents({"id": {"$exists": True}})
    users_without_id = await db.users.count_documents({"id": {"$exists": False}})
    
    print(f"   - Users with 'id' field: {users_with_id}")
    print(f"   - Users without 'id' field: {users_without_id}")
    
    if users_with_id > 0:
        print("\nSample user with 'id' field:")
        user_with_id = await db.users.find_one({"id": {"$exists": True}})
        print(f"   - Email: {user_with_id.get('email')}")
        print(f"   - ID: {user_with_id.get('id')}")
        print(f"   - Name: {user_with_id.get('name')}")
    
    if users_without_id > 0:
        print("\nSample user without 'id' field:")
        user_without_id = await db.users.find_one({"id": {"$exists": False}})
        print(f"   - Email: {user_without_id.get('email')}")
        print(f"   - _id: {user_without_id.get('_id')}")
        print(f"   - Name: {user_without_id.get('name')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_user_fields())