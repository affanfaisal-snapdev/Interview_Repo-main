#!/bin/bash

# Setup script for local development
set -e

echo "🚀 Setting up AI Chatbot Backend..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
fi

# Create database
echo "🗄️  Initializing database..."
python -c "from app.db.base import create_all_tables; create_all_tables()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Run: uvicorn app.main:app --reload"
echo "3. Visit: http://localhost:8000/docs"
echo ""
