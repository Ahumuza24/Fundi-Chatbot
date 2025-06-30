import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self):
        self.db_path = "rag_chatbot.db"
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id)
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def create_user(self, username: str, hashed_password: str, is_admin: bool = False) -> int:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (username, hashed_password, is_admin)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"id": result[0], "username": result[1], "password": result[2], "is_admin": bool(result[3])}
        return None
    
    def create_chat(self, chat_id: str, user_id: int, title: str):
        """Create a new chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (id, user_id, title) VALUES (?, ?, ?)",
            (chat_id, user_id, title)
        )
        conn.commit()
        conn.close()
    
    def save_message(self, chat_id: str, role: str, content: str):
        """Save a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )
        conn.commit()
        conn.close()
    
    def get_user_chats(self, user_id: int) -> List[Dict]:
        """Get all chats for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"id": row[0], "title": row[1], "created_at": row[2]}
            for row in results
        ]
    
    def get_chat_messages(self, chat_id: str, user_id: int) -> List[Dict]:
        """Get all messages for a specific chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.role, m.content, m.timestamp 
            FROM messages m 
            JOIN chats c ON m.chat_id = c.id 
            WHERE c.id = ? AND c.user_id = ? 
            ORDER BY m.timestamp
        ''', (chat_id, user_id))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in results
        ]
    
    def delete_chat(self, chat_id: str, user_id: int):
        """Delete a chat and its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute('''
            DELETE FROM messages 
            WHERE chat_id IN (
                SELECT id FROM chats WHERE id = ? AND user_id = ?
            )
        ''', (chat_id, user_id))
        
        # Delete chat
        cursor.execute(
            "DELETE FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        
        conn.commit()
        conn.close()
    
    def save_document(self, user_id: int, filename: str, content: str) -> int:
        """Save a document to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (user_id, filename, content) VALUES (?, ?, ?)",
            (user_id, filename, content)
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def get_user_documents(self, user_id: int) -> List[Dict]:
        """Get all documents for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, filename, created_at FROM documents WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"id": row[0], "filename": row[1], "created_at": row[2]}
            for row in results
        ]
    
    # Admin methods
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, is_admin, created_at FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"id": result[0], "username": result[1], "is_admin": bool(result[2]), "created_at": result[3]}
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"id": row[0], "username": row[1], "is_admin": bool(row[2]), "created_at": row[3]}
            for row in results
        ]
    
    def update_user(self, user_id: int, username: str, is_admin: bool = False) -> bool:
        """Update user details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET username = ?, is_admin = ? WHERE id = ?",
                (username, is_admin, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def delete_user_chats(self, user_id: int) -> bool:
        """Delete all chats and messages for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete messages first
            cursor.execute('''
                DELETE FROM messages 
                WHERE chat_id IN (
                    SELECT id FROM chats WHERE user_id = ?
                )
            ''', (user_id,))
            
            # Delete chats
            cursor.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user chats: {e}")
            return False
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents from all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.filename, d.created_at, u.username 
            FROM documents d 
            JOIN users u ON d.user_id = u.id 
            ORDER BY d.created_at DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"id": row[0], "filename": row[1], "created_at": row[2], "username": row[3]}
            for row in results
        ]
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict]:
        """Get document by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.filename, d.content, d.created_at, u.username 
            FROM documents d 
            JOIN users u ON d.user_id = u.id 
            WHERE d.id = ?
        ''', (document_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"id": result[0], "filename": result[1], "content": result[2], "created_at": result[3], "username": result[4]}
        return None
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_chat_count(self) -> int:
        """Get total number of chats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chats")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_message_count(self) -> int:
        """Get total number of messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0 