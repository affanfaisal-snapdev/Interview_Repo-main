"""
Pydantic schemas for message-related API requests/responses.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class MessageData(BaseModel):
    """Message data in conversation history."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Message creation timestamp")


class ChatRequest(BaseModel):
    """Request to send a message in a chat session."""

    session_id: str = Field(..., description="Session UUID")
    message: str = Field(..., min_length=1, description="User message text")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "What is the capital of France?",
            }
        }


class ChatResponse(BaseModel):
    """Response from a chat message."""

    session_id: str = Field(..., description="Session UUID")
    user_message: str = Field(..., description="User's input message")
    assistant_message: str = Field(..., description="Assistant's response message")
    conversation_history: List[MessageData] = Field(
        ..., description="Full conversation history including this message"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_message": "What is the capital of France?",
                "assistant_message": "The capital of France is Paris.",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "What is the capital of France?",
                        "created_at": "2026-02-12T10:00:00",
                    },
                    {
                        "role": "assistant",
                        "content": "The capital of France is Paris.",
                        "created_at": "2026-02-12T10:00:01",
                    },
                ],
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Session not found",
                "status_code": 404,
            }
        }
