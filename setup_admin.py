#!/usr/bin/env python3
"""
Script to create an admin user automatically
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime
import bcrypt

# Load environment variables
load_dotenv('/app/backend/.env')

async def setup_admin():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔐 Setting up Admin User")
    print("=" * 40)
    
    # Default admin credentials
    admin_email = "admin@lovable.com"
    admin_password = "admin123"
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": admin_email})
    
    if existing_user:
        print(f"✅ User {admin_email} found.")
        user_id = existing_user["id"]
    else:
        print(f"👤 Creating admin user: {admin_email}")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
        
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "email": admin_email,
            "username": "admin",
            "hashed_password": hashed_password.decode('utf-8'),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": True
        }
        
        await db.users.insert_one(new_user)
        print(f"✅ Created admin user with ID: {user_id}")
    
    # Make user admin
    existing_admin = await db.admin_users.find_one({"user_id": user_id})
    if existing_admin:
        print(f"⚠️ User {admin_email} is already an admin")
    else:
        admin_user = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "role": "admin",
            "created_at": datetime.utcnow(),
            "created_by": "system",
            "is_active": True
        }
        
        await db.admin_users.insert_one(admin_user)
        print(f"🎉 User {admin_email} is now an admin!")
    
    print("\n📋 Admin Login Credentials:")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print(f"Access: /admin")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_admin())