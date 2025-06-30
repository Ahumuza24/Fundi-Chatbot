#!/usr/bin/env python3

import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend API...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server responded with unexpected status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return False
    
    # Test 2: Test registration
    try:
        test_user = {
            "username": "testuser123",
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/register",
            data=test_user,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ User registration working")
            token = response.json().get("token")
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print("✅ User registration working (user already exists)")
            # Try to login instead
            response = requests.post(
                f"{base_url}/api/auth/login",
                data=test_user,
                timeout=10
            )
            if response.status_code == 200:
                token = response.json().get("token")
            else:
                print("❌ Login failed")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False
    
    # Test 3: Test authentication
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/chat/history", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Authentication working")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False
    
    print("🎉 All backend tests passed!")
    return True

if __name__ == "__main__":
    test_backend() 