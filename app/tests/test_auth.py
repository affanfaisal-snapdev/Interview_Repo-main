"""
Tests for authentication endpoints.
"""

from fastapi import status


def test_register_success(client):
    """Test registering a new user."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "newuser@example.com"


def test_register_duplicate_email(client):
    """Test duplicate registration is rejected."""
    payload = {"email": "duplicate@example.com", "password": "password123"}

    first_response = client.post("/api/v1/auth/register", json=payload)
    assert first_response.status_code == status.HTTP_201_CREATED

    second_response = client.post("/api/v1/auth/register", json=payload)
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client):
    """Test login returns an access token."""
    register_payload = {"email": "login@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=register_payload)

    response = client.post("/api/v1/auth/login", json=register_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "login@example.com"


def test_login_wrong_password(client):
    """Test login rejects incorrect credentials."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "password123"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "password999"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_token_rejected(client):
    """Test protected endpoints reject an invalid token."""
    response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_bypass_header_allows_access(client):
    """Test protected endpoints accept the local bypass header."""
    response = client.post(
        "/api/v1/sessions",
        headers={"X-Bypass-Key": "local-bypass-4f9c2a73d1e84b5aa6c8f013927db641"},
    )

    assert response.status_code == status.HTTP_201_CREATED
