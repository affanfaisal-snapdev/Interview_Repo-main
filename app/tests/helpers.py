"""
Shared helpers for authenticated API tests.
"""


def register_and_get_token(
    client,
    email: str = "user@example.com",
    password: str = "password123",
) -> str:
    """
    Register a test user and return a bearer token.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()["access_token"]
