#!/usr/bin/env python3
import sqlite3
import os

def test_database():
    print("Testing database directly...")
    
    db_path = "backend/rag_chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"✗ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check users
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = cursor.fetchall()
        print(f"✓ Users in database: {len(users)}")
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Admin: {user[2]}")
        
        # Check documents
        cursor.execute("SELECT id, user_id, filename, created_at FROM documents")
        documents = cursor.fetchall()
        print(f"✓ Documents in database: {len(documents)}")
        for doc in documents:
            print(f"  - ID: {doc[0]}, User ID: {doc[1]}, Filename: {doc[2]}, Created: {doc[3]}")
        
        # Check document count
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"✓ Total document count: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error accessing database: {e}")

if __name__ == "__main__":
    test_database() 