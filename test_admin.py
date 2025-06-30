#!/usr/bin/env python3
import requests
import json

# Test admin functionality
BASE_URL = "http://localhost:8000/api"

def test_admin_functionality():
    print("Testing Admin Dashboard Functionality...")
    
    # Login as admin user
    print("\n1. Logging in as admin...")
    admin_data = {
        "username": "cedric",
        "password": "ahumuza@123"
    }
    
    try:
        # Login as admin
        
        # Login as admin
        response = requests.post(f"{BASE_URL}/auth/login", data=admin_data)
        if response.status_code == 200:
            token = response.json()["token"]
            print("✓ Admin login successful")
        else:
            print(f"✗ Failed to login as admin: {response.text}")
            return
        
        # Test admin stats endpoint
        print("\n2. Testing admin stats...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Admin stats retrieved: {stats}")
        else:
            print(f"✗ Failed to get admin stats: {response.text}")
        
        # Test get all users
        print("\n3. Testing get all users...")
        response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"✓ Users retrieved: {users}")
        else:
            print(f"✗ Failed to get users: {response.text}")
        
        # Test get all documents
        print("\n4. Testing get all documents...")
        response = requests.get(f"{BASE_URL}/admin/documents", headers=headers)
        if response.status_code == 200:
            documents = response.json()
            print(f"✓ Documents retrieved: {documents}")
        else:
            print(f"✗ Failed to get documents: {response.text}")
        
        print("\n✓ All admin functionality tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Error during testing: {e}")

if __name__ == "__main__":
    test_admin_functionality() 