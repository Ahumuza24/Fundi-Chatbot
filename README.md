# Offline RAG Chatbot

A fully offline Retrieval-Augmented Generation (RAG) chatbot that uses local models via Ollama. The system can ingest PDF and Word documents, embed them using `nomic-embed-text`, and generate responses using `llama3` - all running locally without internet dependency.

## Features

- 🔐 **Authentication System**: JWT-based login and registration
- 📄 **Document Upload**: Support for PDF and DOCX files
- 🧠 **Local AI Models**: Uses Ollama for both embeddings and LLM
- 💾 **Vector Storage**: ChromaDB for local document embeddings
- 💬 **Chat Interface**: ChatGPT-like UI with conversation history
- 🔒 **Fully Offline**: No internet dependency after initial setup
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🛡️ **Robust Error Handling**: User-friendly error messages and graceful failure handling

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **SQLite**: Local database for users, chats, and messages
- **ChromaDB**: Local vector database for embeddings
- **pdfplumber**: PDF text extraction (macOS compatible)
- **python-docx**: Word document text extraction
- **Ollama**: Local model serving (nomic-embed-text, llama3)

### Frontend
- **React**: UI framework
- **TailwindCSS**: Styling
- **Axios**: HTTP client
- **React Router**: Navigation
- **Lucide React**: Icons

## Prerequisites

1. **Python 3.8+** (tested with Python 3.13)
2. **Node.js 16+**
3. **Ollama** installed and running locally

### Installing Ollama

Visit [ollama.ai](https://ollama.ai) and follow the installation instructions for your platform.

After installation, pull the required models:

```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Pull the LLM model
ollama pull llama3
```

## Quick Start

### 1. Start Ollama
```bash
ollama serve
```

### 2. Start the Application
```bash
./start-app.sh
```

This will start both the backend and frontend servers automatically.

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### 4. Test the Backend (Optional)
```bash
./test-backend.py
```

## Manual Setup (if needed)

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (uses pdfplumber for macOS compatibility)
pip install -r requirements-python313.txt

# Copy the pdfplumber-based document processor
cp document_processor_alternative.py document_processor.py

# Start the server
python main.py
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Usage

1. **Register/Login**: Create an account or sign in
2. **Upload Documents**: Use the upload button to add PDF or DOCX files
3. **Start Chatting**: Ask questions about your uploaded documents
4. **Chat History**: Access previous conversations from the sidebar

## Error Handling

The application includes comprehensive error handling:

### Backend Error Handling
- **Global Exception Handler**: Prevents internal errors from being exposed to users
- **Input Validation**: Validates all user inputs with helpful error messages
- **Graceful Degradation**: Handles network issues and service failures
- **Detailed Logging**: All errors are logged for debugging while showing user-friendly messages

### Frontend Error Handling
- **Network Error Detection**: Handles connection issues gracefully
- **User-Friendly Messages**: Technical errors are translated to understandable messages
- **Authentication Recovery**: Automatically redirects to login on auth failures
- **Loading States**: Shows appropriate loading indicators during operations

### Common Error Scenarios Handled
- ✅ Network connectivity issues
- ✅ Authentication token expiration
- ✅ Invalid file uploads
- ✅ Server errors
- ✅ Database connection issues
- ✅ Ollama service unavailability

## Project Structure

```
MCP/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── auth.py                    # Authentication handler
│   ├── database.py                # Database operations
│   ├── document_processor.py      # Document text extraction (pdfplumber)
│   ├── rag_engine.py              # RAG implementation
│   ├── requirements-python313.txt # Python dependencies
│   └── venv/                      # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── contexts/              # React contexts
│   │   └── App.js                # Main app component
│   ├── package.json              # Node dependencies
│   └── node_modules/             # Installed packages
├── start-app.sh                  # Quick start script
├── test-backend.py               # Backend testing script
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Documents
- `POST /api/documents/upload` - Upload document

### Chat
- `POST /api/chat/query` - Send message and get response
- `GET /api/chat/history` - Get user's chat history
- `GET /api/chat/{chat_id}/messages` - Get messages for specific chat
- `DELETE /api/chat/{chat_id}` - Delete chat

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if models are pulled: `ollama list`

2. **Port Conflicts**
   - Backend runs on port 8000
   - Frontend runs on port 3000

3. **PDF Processing Issues**
   - The system uses `pdfplumber` which is more compatible with macOS
   - If you encounter issues, try uploading DOCX files instead

4. **Python Version Issues**
   - The system is tested with Python 3.13
   - Use `requirements-python313.txt` for the latest compatible versions

5. **Authentication Errors**
   - Clear browser storage if you encounter token issues
   - Restart the application if authentication problems persist

### Performance Tips

- Use SSD storage for better ChromaDB performance
- Ensure sufficient RAM for Ollama models
- Consider using smaller models for faster responses

### Testing

Run the test script to verify everything is working:

```bash
./test-backend.py
```

This will test:
- ✅ Backend server connectivity
- ✅ User registration/login
- ✅ Authentication token validation
- ✅ API endpoint functionality

## Security Notes

- Change the default SECRET_KEY in production
- The system is designed for local/private use
- JWT tokens expire after 30 minutes
- All data is stored locally
- Input validation prevents common security issues

## Recent Fixes

- ✅ **Fixed bcrypt compatibility** with Python 3.13
- ✅ **Improved error handling** with user-friendly messages
- ✅ **Added comprehensive logging** for debugging
- ✅ **Enhanced input validation** for better security
- ✅ **Fixed PDF processing** with pdfplumber for macOS compatibility

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Ollama](https://ollama.ai) for local model serving
- [ChromaDB](https://chromadb.com) for vector storage
- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [React](https://reactjs.org) for the frontend framework 