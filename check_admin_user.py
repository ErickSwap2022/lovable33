#!/usr/bin/env python3
"""
Script to check admin user in database and create if needed
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(mongo_url)
db = client["emergent"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_and_create_admin():
    """Check if admin user exists and create if needed"""
    
    # Check if admin user exists
    admin_user = await db.users.find_one({"email": "admin@lovable.com"})
    
    if admin_user:
        print("✅ Admin user found in database:")
        print(f"   Email: {admin_user.get('email')}")
        print(f"   ID: {admin_user.get('id')}")
        print(f"   Name: {admin_user.get('name', 'NOT SET')}")
        print(f"   Username: {admin_user.get('username', 'NOT SET')}")
        print(f"   Created: {admin_user.get('created_at', 'NOT SET')}")
        
        # Check if name field is missing and add it
        if 'name' not in admin_user:
            print("⚠️  Admin user missing 'name' field. Adding it...")
            await db.users.update_one(
                {"email": "admin@lovable.com"},
                {"$set": {"name": "Admin User", "updated_at": datetime.utcnow()}}
            )
            print("✅ Added 'name' field to admin user")
        
        # Check if admin_users collection has this user
        admin_record = await db.admin_users.find_one({"user_id": admin_user["id"]})
        if admin_record:
            print("✅ Admin privileges found in admin_users collection")
        else:
            print("⚠️  Admin user not found in admin_users collection. Adding...")
            admin_data = {
                "user_id": admin_user["id"],
                "role": "admin",
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            await db.admin_users.insert_one(admin_data)
            print("✅ Added admin privileges to admin_users collection")
    
    else:
        print("❌ Admin user not found. Creating admin user...")
        
        # Create admin user
        admin_data = {
            "id": str(uuid.uuid4()),
            "email": "admin@lovable.com",
            "name": "Admin User",
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_premium": True,
            "projects_count": 0,
            "followers_count": 0,
            "following_count": 0
        }
        
        await db.users.insert_one(admin_data)
        print("✅ Created admin user in users collection")
        
        # Add admin privileges
        admin_privileges = {
            "user_id": admin_data["id"],
            "role": "admin",
            "created_by": "system",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await db.admin_users.insert_one(admin_privileges)
        print("✅ Added admin privileges to admin_users collection")
        
        print(f"✅ Admin user created with ID: {admin_data['id']}")

async def main():
    try:
        await check_and_create_admin()
        print("\n🎉 Admin user setup completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())