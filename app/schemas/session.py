"""
Pydantic schemas for session-related API requests/responses.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    """Request to create a new chat session."""

    pass  # No fields required for basic session creation


class SessionCreateResponse(BaseModel):
    """Response after creating a new session."""

    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")

    class Config:
        from_attributes = True


class SessionInfoResponse(BaseModel):
    """Response containing session information."""

    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in session")

    class Config:
        from_attributes = True
