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
    
    def create_user(self, username: str, hashed_password: str) -> int:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"id": result[0], "username": result[1], "password": result[2]}
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