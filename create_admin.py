#!/usr/bin/env python3
"""
Script to create an admin user
Run this to make an existing user an admin or create a new admin user
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

async def create_admin():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔐 Creating Admin User")
    print("=" * 40)
    
    # Ask for user info
    email = input("Enter email address for admin user: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": email})
    
    if existing_user:
        print(f"✅ User {email} found. Making them admin...")
        user_id = existing_user["id"]
    else:
        print(f"👤 User {email} not found. Creating new admin user...")
        
        # Create new user
        password = input("Enter password for new admin user: ").strip()
        if not password:
            print("❌ Password is required")
            return
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "email": email,
            "username": "admin",
            "hashed_password": hashed_password.decode('utf-8'),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": True
        }
        
        await db.users.insert_one(new_user)
        print(f"✅ Created new user with ID: {user_id}")
    
    # Make user admin
    admin_user = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "role": "admin",
        "created_at": datetime.utcnow(),
        "created_by": "system",
        "is_active": True
    }
    
    # Check if already admin
    existing_admin = await db.admin_users.find_one({"user_id": user_id})
    if existing_admin:
        print(f"⚠️ User {email} is already an admin")
    else:
        await db.admin_users.insert_one(admin_user)
        print(f"🎉 User {email} is now an admin!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())