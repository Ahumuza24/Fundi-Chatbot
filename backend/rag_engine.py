import requests
import json
import numpy as np
from typing import List, Dict
import chromadb
from chromadb.config import Settings
import os

class RAGEngine:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.embedding_model = "nomic-embed-text"
        self.llm_model = "llama3"
        self.chroma_client = None
        self.collection = None
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Warning: Could not initialize ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using nomic-embed-text via Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                raise Exception(f"Embedding API error: {response.status_code}")
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    def add_document(self, text: str, filename: str, user_id: int) -> str:
        """Add a document to the vector store"""
        if not self.collection:
            raise Exception("ChromaDB not initialized")
        
        # Chunk the text
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        chunks = processor.chunk_text(text)
        
        # Generate embeddings for each chunk
        embeddings = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk)
            embeddings.append(embedding)
            
            metadata = {
                "filename": filename,
                "user_id": user_id,
                "chunk_index": i,
                "text_length": len(chunk)
            }
            metadatas.append(metadata)
            
            # Generate unique ID
            doc_id = f"{filename}_{user_id}_{i}"
            ids.append(doc_id)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Added {len(chunks)} chunks from {filename}"
    
    def search_documents(self, query: str, user_id: int, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        if not self.collection:
            return []
        
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"user_id": user_id}
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return documents
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, query: str, relevant_docs: List[Dict]) -> str:
        """Generate response using llama3 via Ollama"""
        try:
            # Prepare context from relevant documents
            context = ""
            if relevant_docs:
                context = "Based on the following information:\n\n"
                for i, doc in enumerate(relevant_docs[:3]):  # Use top 3 docs
                    context += f"Document {i+1}:\n{doc['content']}\n\n"
            
            # Create prompt
            prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context. If the context doesn't contain relevant information, say so politely.

{context}
User Question: {query}

Answer:"""
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error generating response: {response.status_code}"
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    def delete_user_documents(self, user_id: int):
        """Delete all documents for a user"""
        if not self.collection:
            return
        
        try:
            # Get all documents for the user
            results = self.collection.get(
                where={"user_id": user_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                
        except Exception as e:
            print(f"Error deleting user documents: {e}") 