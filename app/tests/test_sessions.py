"""
Tests for session management endpoints.
"""

import pytest
from fastapi import status


def test_create_session(client):
    """Test creating a new session."""
    response = client.post("/api/v1/sessions")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert "session_id" in data
    assert "created_at" in data
    assert len(data["session_id"]) == 36  # UUID format


def test_get_session(client):
    """Test retrieving session information."""
    # Create a session
    create_response = client.post("/api/v1/sessions")
    session_id = create_response.json()["session_id"]

    # Retrieve the session
    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["session_id"] == session_id
    assert "created_at" in data
    assert data["message_count"] == 0


def test_get_nonexistent_session(client):
    """Test retrieving a non-existent session."""
    response = client.get(
        "/api/v1/sessions/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_multiple_sessions(client):
    """Test creating multiple sessions."""
    session_ids = set()

    for _ in range(3):
        response = client.post("/api/v1/sessions")
        assert response.status_code == status.HTTP_201_CREATED
        session_ids.add(response.json()["session_id"])

    # All session IDs should be unique
    assert len(session_ids) == 3
