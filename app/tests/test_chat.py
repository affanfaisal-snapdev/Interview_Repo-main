"""
Tests for chat endpoints.
"""

from unittest.mock import AsyncMock, patch

from fastapi import status

from app.tests.helpers import register_and_get_token


def test_send_message_success(client):
    """Test sending a message to a chat session."""
    token = register_and_get_token(client)

    # Create a session
    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    with patch(
        "app.api.routers.chat.langgraph_service.execute_chat",
        new=AsyncMock(return_value="This is a test response from Gemini."),
    ):
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "Hello, how are you?",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == session_id
        assert data["user_message"] == "Hello, how are you?"
        assert "assistant_message" in data
        assert isinstance(data["conversation_history"], list)


def test_send_message_answers_products_query_with_nl_to_sql(client, db):
    """Chat should answer products/orders questions from the ecommerce tables."""
    token = register_and_get_token(client)

    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    with patch(
        "app.api.routers.chat.langgraph_service.execute_chat",
        new=AsyncMock(
            return_value=(
                "I found 2 matching record(s):\n"
                "- name=Luna Smart Watch, price=149.0\n"
                "- name=Aurora Wireless Headphones, price=129.99"
            )
        ),
    ):
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "Show me the two most expensive products",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "assistant_message" in data
    assert "I found 2 matching record(s):" in data["assistant_message"]
    assert "Luna Smart Watch" in data["assistant_message"]
    assert "Aurora Wireless Headphones" in data["assistant_message"]


def test_send_message_falls_back_when_query_is_not_for_products_or_orders(client):
    """Non-ecommerce chat should continue through the existing assistant flow."""
    token = register_and_get_token(client)

    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    with patch(
        "app.api.routers.chat.langgraph_service.execute_chat",
        new=AsyncMock(return_value="This is a test response from Gemini."),
    ):
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "What is the capital of France?",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["assistant_message"] == "This is a test response from Gemini."


def test_send_message_returns_upstream_error(client):
    """Test upstream model failures return an HTTP error instead of fake assistant text."""
    token = register_and_get_token(client)

    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    with patch(
        "app.api.routers.chat.langgraph_service.execute_chat",
        new=AsyncMock(side_effect=RuntimeError("Gemini API HTTP error: 401")),
    ):
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "Hello, how are you?",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.json()["detail"] == "Workflow execution failed: Gemini API HTTP error: 401"


def test_send_message_to_nonexistent_session(client):
    """Test sending a message to a non-existent session."""
    token = register_and_get_token(client)
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "message": "Hello",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_send_empty_message(client):
    """Test sending an empty message."""
    token = register_and_get_token(client)

    # Create a session
    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    # Send empty message
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should fail validation
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_conversation_history(client):
    """Test that conversation history is maintained."""
    token = register_and_get_token(client)

    # Create a session
    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    # Mock multiple messages
    messages = [
        "First message",
        "Second message",
        "Third message",
    ]

    with patch(
        "app.api.routers.chat.langgraph_service.execute_chat",
        new=AsyncMock(return_value="Response message"),
    ):
        # Send multiple messages
        for message in messages:
            response = client.post(
                "/api/v1/chat/message",
                json={
                    "session_id": session_id,
                    "message": message,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify conversation history grows
            expected_count = (messages.index(message) + 1) * 2
            assert len(data["conversation_history"]) == expected_count


def test_message_validation(client):
    """Test message validation."""
    token = register_and_get_token(client)

    # Create a session
    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = session_response.json()["session_id"]

    # Test missing session_id
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test missing message
    response = client.post(
        "/api/v1/chat/message",
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_send_message_requires_auth(client):
    """Test chat endpoint requires a bearer token."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "message": "Hello",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_other_user_cannot_chat_in_session(client):
    """Test a user cannot send messages to another user's session."""
    owner_token = register_and_get_token(client, "chatowner@example.com")
    other_token = register_and_get_token(client, "chatother@example.com")

    session_response = client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    session_id = session_response.json()["session_id"]

    response = client.post(
        "/api/v1/chat/message",
        json={"session_id": session_id, "message": "Hello"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
