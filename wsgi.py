"""
Application entry point for running with Gunicorn.

Usage: gunicorn wsgi:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
