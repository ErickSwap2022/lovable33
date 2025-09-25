#!/usr/bin/env python3
"""
Test admin service directly
"""

import sys
sys.path.append('/app/backend')

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from services.admin_service import AdminService

async def test_admin_service():
    # MongoDB connection
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["emergent"]
    
    admin_service = AdminService(db)
    
    try:
        print("🔍 Testing get_users_management...")
        users = await admin_service.get_users_management(0, 50)
        print(f"✅ Users retrieved: {len(users)}")
        for user in users[:3]:  # Show first 3 users
            print(f"   - {user.email} (ID: {user.id})")
    except Exception as e:
        print(f"❌ Error in get_users_management: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
    
    try:
        print("\n🔍 Testing get_projects_management...")
        projects = await admin_service.get_projects_management(0, 50)
        print(f"✅ Projects retrieved: {len(projects)}")
        for project in projects[:3]:  # Show first 3 projects
            print(f"   - {project.name} (Owner: {project.owner_email})")
    except Exception as e:
        print(f"❌ Error in get_projects_management: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_admin_service())