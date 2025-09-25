#!/usr/bin/env python3
"""
Debug admin endpoints
"""

import requests
import json

BACKEND_URL = "https://devsage-2.preview.emergentagent.com/api"

def test_admin_endpoints():
    # First login as admin
    login_data = {
        "email": "admin@lovable.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Admin login successful")
    
    # Test admin users endpoint
    print("\n🔍 Testing admin users endpoint...")
    response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test admin projects endpoint
    print("\n🔍 Testing admin projects endpoint...")
    response = requests.get(f"{BACKEND_URL}/admin/projects", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_admin_endpoints()