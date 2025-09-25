#!/usr/bin/env python3
"""
Check database structure
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db_structure():
    # MongoDB connection
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["emergent"]
    
    print("🔍 Checking users collection structure...")
    user_sample = await db.users.find_one()
    if user_sample:
        print("Sample user document fields:")
        for key in user_sample.keys():
            print(f"   - {key}: {type(user_sample[key])}")
    else:
        print("No users found in database")
    
    print("\n🔍 Checking projects collection structure...")
    project_sample = await db.projects.find_one()
    if project_sample:
        print("Sample project document fields:")
        for key in project_sample.keys():
            print(f"   - {key}: {type(project_sample[key])}")
    else:
        print("No projects found in database")
    
    print(f"\n📊 Collection counts:")
    print(f"   - Users: {await db.users.count_documents({})}")
    print(f"   - Projects: {await db.projects.count_documents({})}")
    print(f"   - Admin users: {await db.admin_users.count_documents({})}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_db_structure())