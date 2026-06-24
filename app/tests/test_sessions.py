"""
Tests for session management endpoints.
"""

from fastapi import status

from app.tests.helpers import register_and_get_token


def test_create_session(client):
    """Test creating a new session."""
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert "session_id" in data
    assert "created_at" in data
    assert len(data["session_id"]) == 36  # UUID format


def test_get_session(client):
    """Test retrieving session information."""
    token = register_and_get_token(client)

    # Create a session
    create_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = create_response.json()["session_id"]

    # Retrieve the session
    response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["session_id"] == session_id
    assert "created_at" in data
    assert data["message_count"] == 0


def test_get_nonexistent_session(client):
    """Test retrieving a non-existent session."""
    token = register_and_get_token(client)
    response = client.get(
        "/api/v1/sessions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_multiple_sessions(client):
    """Test creating multiple sessions."""
    token = register_and_get_token(client)
    session_ids = set()

    for _ in range(3):
        response = client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        session_ids.add(response.json()["session_id"])

    # All session IDs should be unique
    assert len(session_ids) == 3


def test_create_session_requires_auth(client):
    """Test session creation requires a bearer token."""
    response = client.post("/api/v1/sessions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_session_is_hidden_from_other_users(client):
    """Test users cannot access sessions owned by someone else."""
    owner_token = register_and_get_token(client, "owner@example.com")
    other_token = register_and_get_token(client, "other@example.com")

    create_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    session_id = create_response.json()["session_id"]

    response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_bypass_key_can_access_any_session(client):
    """Test the bypass header can access a session created by another user."""
    owner_token = register_and_get_token(client, "bypass-owner@example.com")
    create_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    session_id = create_response.json()["session_id"]

    response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"X-Bypass-Key": "local-bypass-4f9c2a73d1e84b5aa6c8f013927db641"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["session_id"] == session_id
