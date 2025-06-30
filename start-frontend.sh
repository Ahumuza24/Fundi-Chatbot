#!/bin/bash

echo "🚀 Starting Frontend Server..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not found. Run setup.sh first."
    exit 1
fi

# Start the development server
npm start 