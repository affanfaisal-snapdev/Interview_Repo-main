"""
Pydantic schemas for authentication endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request payload for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class LoginRequest(BaseModel):
    """Request payload for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class AuthenticatedUserResponse(BaseModel):
    """User information returned after authentication."""

    id: str = Field(..., description="User identifier")
    email: EmailStr = Field(..., description="User email address")
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")
    user: AuthenticatedUserResponse = Field(..., description="Authenticated user")
