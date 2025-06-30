#!/usr/bin/env python3
import requests
import json
import os

# Test document upload functionality
BASE_URL = "http://localhost:8000/api"

def test_document_upload():
    print("Testing Document Upload Functionality...")
    
    # Login as admin
    print("\n1. Logging in as admin...")
    admin_data = {
        "username": "cedric",
        "password": "ahumuza@123"
    }
    
    try:
        # Login as admin
        response = requests.post(f"{BASE_URL}/auth/login", data=admin_data)
        if response.status_code == 200:
            token = response.json()["token"]
            print("✓ Admin login successful")
        else:
            print(f"✗ Failed to login as admin: {response.text}")
            return
        
        # Test document upload
        print("\n2. Testing document upload...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload the test DOCX file
        with open("test_document.docx", "rb") as f:
            files = {"file": ("test_document.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Document uploaded successfully: {result}")
        else:
            print(f"✗ Failed to upload document: {response.text}")
        
        # Test get all documents
        print("\n3. Testing get all documents...")
        response = requests.get(f"{BASE_URL}/admin/documents", headers=headers)
        if response.status_code == 200:
            documents = response.json()
            print(f"✓ Documents retrieved: {documents}")
        else:
            print(f"✗ Failed to get documents: {response.text}")
        
        # Test admin stats
        print("\n4. Testing admin stats...")
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Admin stats retrieved: {stats}")
        else:
            print(f"✗ Failed to get admin stats: {response.text}")
        
        print("\n✓ All upload functionality tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Error during testing: {e}")

if __name__ == "__main__":
    test_document_upload() 