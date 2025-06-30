import os
os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
from typing import List, Optional
import requests
import sqlite3
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import uuid
import logging
import traceback

from auth import AuthHandler
from document_processor import DocumentProcessor
from rag_engine import RAGEngine
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Offline RAG Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
auth_handler = AuthHandler()
document_processor = DocumentProcessor()
rag_engine = RAGEngine()
db_manager = DatabaseManager()

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Initialize database and check Ollama connection"""
    try:
        db_manager.init_database()
        # Check if Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                logger.warning("Ollama is not running. Please start Ollama first.")
        except requests.exceptions.RequestException:
            logger.warning("Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to prevent internal errors from being exposed"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.post("/api/auth/register")
async def register(username: str = Form(...), password: str = Form(...)):
    """Register a new user"""
    try:
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        if db_manager.user_exists(username):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = auth_handler.get_password_hash(password)
        user_id = db_manager.create_user(username, hashed_password)
        
        token = auth_handler.create_token(user_id, username)
        return {"token": token, "user_id": user_id, "username": username}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login user"""
    try:
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        user = db_manager.get_user_by_username(username)
        if not user or not auth_handler.verify_password(password, user['password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_handler.create_token(user['id'], username)
        return {"token": token, "user_id": user['id'], "username": username}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = auth_handler.decode_token(credentials.credentials)
        user_id = payload.get("user_id")
        username = payload.get("username")
        if user_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Save file temporarily
        file_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text
        text = document_processor.extract_text(file_path)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the document")
        
        # Generate embeddings and store
        document_id = rag_engine.add_document(text, file.filename, current_user["user_id"])
        
        # Clean up temp file
        os.remove(file_path)
        
        return {"message": "Document uploaded successfully", "document_id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Clean up temp file if it exists
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail="Document upload failed. Please try again.")

@app.post("/api/chat/query")
async def query_chat(
    message: str = Form(...),
    chat_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Process a chat query using RAG"""
    try:
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create new chat if none provided
        if not chat_id:
            chat_id = str(uuid.uuid4())
            db_manager.create_chat(chat_id, current_user["user_id"], message[:50])
        
        # Get relevant documents
        relevant_docs = rag_engine.search_documents(message, current_user["user_id"])
        
        # Generate response using LLM
        response = rag_engine.generate_response(message, relevant_docs)
        
        # Save messages to database
        db_manager.save_message(chat_id, "user", message)
        db_manager.save_message(chat_id, "assistant", response)
        
        return {
            "response": response,
            "chat_id": chat_id,
            "relevant_docs": relevant_docs
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to process your message. Please try again.")

@app.get("/api/chat/history")
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    """Get user's chat history"""
    try:
        chats = db_manager.get_user_chats(current_user["user_id"])
        return {"chats": chats}
    except Exception as e:
        logger.error(f"Chat history error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to load chat history")

@app.get("/api/chat/{chat_id}/messages")
async def get_chat_messages(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a specific chat"""
    try:
        messages = db_manager.get_chat_messages(chat_id, current_user["user_id"])
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Chat messages error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to load messages")

@app.delete("/api/chat/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a chat"""
    try:
        db_manager.delete_chat(chat_id, current_user["user_id"])
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        logger.error(f"Delete chat error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 