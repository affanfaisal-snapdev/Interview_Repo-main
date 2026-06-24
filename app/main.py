"""
FastAPI application for AI chatbot backend system.

This is the main entry point for the application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import sessions, chat
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import create_all_tables

# Setup logging
logger = setup_logging(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown context manager.
    """
    # Startup
    logger.info(f"Starting application in {settings.APP_ENV} mode")
    create_all_tables()
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """
    Factory function to create and configure FastAPI application.
    """
    app = FastAPI(
        title="AI Chatbot Backend",
        description="Production-grade chatbot system with LangGraph and Gemini API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "environment": settings.APP_ENV,
            "version": "1.0.0",
        }

    # Include routers
    app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

    logger.info("Application created successfully")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
