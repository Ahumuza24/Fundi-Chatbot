import os
import uuid
from typing import List, Dict, Optional
from database import DatabaseManager
from rag_engine import RAGEngine
from auth import AuthHandler

class AdminManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.rag_engine = RAGEngine()
        self.auth_handler = AuthHandler()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        try:
            user = self.db_manager.get_user_by_id(user_id)
            return user and user.get('is_admin', False)
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        try:
            return self.db_manager.get_all_users()
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID (admin only)"""
        try:
            return self.db_manager.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user(self, user_id: int, username: str, is_admin: bool = False) -> bool:
        """Update user details (admin only)"""
        try:
            return self.db_manager.update_user(user_id, username, is_admin)
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def reset_user_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (admin only)"""
        try:
            hashed_password = self.auth_handler.get_password_hash(new_password)
            return self.db_manager.update_user_password(user_id, hashed_password)
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and all their data (admin only)"""
        try:
            # Delete user's documents from RAG engine
            self.rag_engine.delete_user_documents(user_id)
            
            # Delete user's chats and messages
            self.db_manager.delete_user_chats(user_id)
            
            # Delete user account
            return self.db_manager.delete_user(user_id)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> Optional[int]:
        """Create a new user (admin only)"""
        try:
            if self.db_manager.user_exists(username):
                return None
            
            hashed_password = self.auth_handler.get_password_hash(password)
            return self.db_manager.create_user(username, hashed_password, is_admin)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents from all users (admin only)"""
        try:
            return self.db_manager.get_all_documents()
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a specific document (admin only)"""
        try:
            # Get document info first
            document = self.db_manager.get_document_by_id(document_id)
            if not document:
                return False
            
            # Delete from RAG engine
            self.rag_engine.delete_document_by_id(document_id)
            
            # Delete from database
            return self.db_manager.delete_document(document_id)
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_system_stats(self) -> Dict:
        """Get system statistics (admin only)"""
        try:
            total_users = self.db_manager.get_user_count()
            total_documents = self.db_manager.get_document_count()
            total_chats = self.db_manager.get_chat_count()
            total_messages = self.db_manager.get_message_count()
            
            return {
                "total_users": total_users,
                "total_documents": total_documents,
                "total_chats": total_chats,
                "total_messages": total_messages
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {
                "total_users": 0,
                "total_documents": 0,
                "total_chats": 0,
                "total_messages": 0
            } 