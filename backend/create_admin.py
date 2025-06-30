#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from auth import AuthHandler

def create_admin_user():
    """Create the first admin user"""
    db_manager = DatabaseManager()
    auth_handler = AuthHandler()
    
    # Initialize database
    db_manager.init_database()
    
    print("=== Create Admin User ===")
    print("This will create the first admin user for the RAG Chatbot system.")
    print()
    
    # Get admin details
    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    if len(username) < 3:
        print("Username must be at least 3 characters long!")
        return
    
    # Check if user already exists
    if db_manager.user_exists(username):
        print(f"User '{username}' already exists!")
        return
    
    password = input("Enter admin password: ").strip()
    if not password:
        print("Password cannot be empty!")
        return
    
    if len(password) < 6:
        print("Password must be at least 6 characters long!")
        return
    
    confirm_password = input("Confirm admin password: ").strip()
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    try:
        # Create admin user
        hashed_password = auth_handler.get_password_hash(password)
        user_id = db_manager.create_user(username, hashed_password, is_admin=True)
        
        print(f"\n✅ Admin user '{username}' created successfully!")
        print(f"User ID: {user_id}")
        print(f"Admin privileges: Enabled")
        print("\nYou can now log in to the admin dashboard.")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user() 