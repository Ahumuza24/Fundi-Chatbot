#!/bin/bash

echo "🚀 Setting up Offline RAG Chatbot for macOS..."

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

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install macOS-specific dependencies
echo "📦 Installing macOS-compatible dependencies..."
pip install -r requirements-macos.txt

# If PyMuPDF-binary fails, try alternative approach
if [ $? -ne 0 ]; then
    echo "⚠️  PyMuPDF-binary failed, trying alternative installation..."
    pip install --upgrade pip setuptools wheel
    pip install PyMuPDF==1.23.8 --no-build-isolation
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