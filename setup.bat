@echo off
REM Setup script for Windows development

echo.
echo 🚀 Setting up AI Chatbot Backend...
echo.

REM Check Python version
python --version
echo ✓ Python installed
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📥 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel > nul

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo ⚙️  Setting up .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your GEMINI_API_KEY
)

REM Create database
echo 🗄️  Initializing database...
python -c "from app.db.base import create_all_tables; create_all_tables()"

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your GEMINI_API_KEY
echo 2. Run: uvicorn app.main:app --reload
echo 3. Visit: http://localhost:8000/docs
echo.
