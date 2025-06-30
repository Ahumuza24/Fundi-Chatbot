#!/bin/bash

echo "🚀 Setting up Offline RAG Chatbot for macOS (with fallback options)..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first from https://ollama.ai"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Try different PDF library approaches
echo "📦 Installing dependencies with PDF processing..."

# First, try the alternative approach with pdfplumber
echo "🔄 Attempting installation with pdfplumber..."
pip install -r requirements-alternative.txt

if [ $? -eq 0 ]; then
    echo "✅ Successfully installed with pdfplumber"
    # Copy the alternative document processor
    cp document_processor_alternative.py document_processor.py
else
    echo "⚠️  pdfplumber installation failed, trying PyMuPDF-binary..."
    pip install -r requirements-macos.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully installed with PyMuPDF-binary"
    else
        echo "⚠️  PyMuPDF-binary failed, trying PyMuPDF with no build isolation..."
        pip install PyMuPDF==1.23.8 --no-build-isolation
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully installed PyMuPDF with no build isolation"
        else
            echo "⚠️  All PDF library installations failed. Installing without PDF support..."
            # Install everything except PDF libraries
            pip install fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-docx==1.1.0 chromadb==0.4.18 numpy==1.24.3 requests==2.31.0 sqlalchemy==2.0.23 pydantic==2.5.0 python-dotenv==1.0.0
            
            echo "⚠️  PDF processing will not be available. Only DOCX files will be supported."
        fi
    fi
fi

echo "✅ Backend setup complete"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
npm install

echo "✅ Frontend setup complete"

# Pull Ollama models
echo "🤖 Pulling Ollama models..."
ollama pull nomic-embed-text
ollama pull llama3

echo "✅ Ollama models ready"

# Make scripts executable
chmod +x ../backend/start.sh
chmod +x ../frontend/start.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start Ollama: ollama serve"
echo "2. Start backend: cd backend && ./start.sh"
echo "3. Start frontend: cd frontend && ./start.sh"
echo ""
echo "Or use the provided scripts:"
echo "./start-backend.sh"
echo "./start-frontend.sh" 