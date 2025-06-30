You are helping me develop an offline RAG (Retrieval-Augmented Generation) chatbot using local models with Ollama. The chatbot will ingest documents (PDF and Word), embed them using `nomic-embed-text`, store them locally, and use `llama3` for answering user queries based on those documents. I want full control over all components.

Project Requirements:

1. **Tech Stack**:
   - Backend: Python (FastAPI)
   - Frontend: React + TailwindCSS
   - Embedding model: `nomic-embed-text` via Ollama
   - LLM: `llama3` via Ollama
   - Vector Store: Local (use `Chroma` or `FAISS`)
   - File ingestion: `.pdf`, `.docx`
   - UI Library: shadcn/ui or Tailwind + Headless UI
   - Authentication: Simple JWT-based login system
   - Memory: Store user chat history in a local database (SQLite or TinyDB)
   - Chat UI: Like ChatGPT’s UI (left panel for past chats, main panel for current thread)

2. **Key Features**:
   - Authentication system with login page and sign up page
   - Upload documents in `.pdf` or `.docx` formats
   - Extract text using PyMuPDF (for PDFs) and python-docx (for Word)
   - Embed documents using `nomic-embed-text` through Ollama
   - Store embeddings in local vector store (e.g., ChromaDB)
   - When a user asks a question, retrieve top relevant chunks using cosine similarity
   - Pass context to `llama3` running locally via Ollama
   - Display response in a chat interface
   - Store chat history locally and display past conversations
   - Keep everything offline; no internet dependency

3. **Architecture**:
   - React frontend for UI
   - FastAPI backend to:
     - Handle auth
     - Handle document upload and text extraction
     - Generate and store embeddings
     - Handle RAG-based queries via Ollama
     - Save and retrieve chat history
   - Ollama runs locally to serve both LLM and embed models

4. **User Flow**:
   - User logs in
   - Uploads documents
   - Documents are embedded and stored locally
   - User asks a question
   - Backend retrieves relevant docs using vector store
   - Sends prompt with context to `llama3` via Ollama API
   - Response shown in chat window
   - Conversation is saved to memory

5. **Frontend Design**:
   - Clean, minimal UI like ChatGPT
   - Left sidebar: list of chat sessions (titles auto-generated from first message)
   - Main view: Chat messages (user & AI), input box, send button
   - Modal or dropdown for uploading new documents
   - Simple login screen

Generate the folder structure, initial setup, and key starter files for both the FastAPI backend and the React frontend. Scaffold authentication, document ingestion, Ollama integration, and embedding via `nomic-embed-text`. Build an MVP that runs fully offline.

Begin with:
- Backend: Auth endpoints, document upload/processing, embedding logic
- Frontend: Auth UI, Chat UI, Document upload button, chat interface with chat history

Make sure the generated code works completely offline.