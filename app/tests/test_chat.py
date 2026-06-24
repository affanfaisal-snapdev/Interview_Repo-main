"""
Tests for chat endpoints.

Note: These tests require mocking the Gemini API calls.
"""

import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


def test_send_message_success(client):
    """Test sending a message to a chat session."""
    # Create a session
    session_response = client.post("/api/v1/sessions")
    session_id = session_response.json()["session_id"]

    # Mock the Gemini API call
    with patch(
        "app.langgraph.nodes.ChatNodes.call_gemini_node"
    ) as mock_gemini:
        # Make the node function return a state with assistant response
        def mock_gemini_call(state):
            messages = state.get("messages", [])
            messages.append({
                "role": "assistant",
                "content": "This is a test response from Gemini."
            })
            return {"messages": messages}

        mock_gemini.side_effect = mock_gemini_call

        # Send a message
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "Hello, how are you?",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == session_id
        assert data["user_message"] == "Hello, how are you?"
        assert "assistant_message" in data
        assert isinstance(data["conversation_history"], list)


def test_send_message_to_nonexistent_session(client):
    """Test sending a message to a non-existent session."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "message": "Hello",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_send_empty_message(client):
    """Test sending an empty message."""
    # Create a session
    session_response = client.post("/api/v1/sessions")
    session_id = session_response.json()["session_id"]

    # Send empty message
    response = client.post(
        "/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "",
        },
    )

    # Should fail validation
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_conversation_history(client):
    """Test that conversation history is maintained."""
    # Create a session
    session_response = client.post("/api/v1/sessions")
    session_id = session_response.json()["session_id"]

    # Mock multiple messages
    messages = [
        "First message",
        "Second message",
        "Third message",
    ]

    with patch(
        "app.langgraph.nodes.ChatNodes.call_gemini_node"
    ) as mock_gemini:
        def mock_gemini_call(state):
            msg_list = state.get("messages", [])
            msg_list.append({
                "role": "assistant",
                "content": "Response message"
            })
            return {"messages": msg_list}

        mock_gemini.side_effect = mock_gemini_call

        # Send multiple messages
        for message in messages:
            response = client.post(
                "/api/v1/chat/message",
                json={
                    "session_id": session_id,
                    "message": message,
                },
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify conversation history grows
            expected_count = len(messages) * 2  # user + assistant for each
            assert len(data["conversation_history"]) == expected_count


def test_message_validation(client):
    """Test message validation."""
    # Create a session
    session_response = client.post("/api/v1/sessions")
    session_id = session_response.json()["session_id"]

    # Test missing session_id
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test missing message
    response = client.post(
        "/api/v1/chat/message",
        json={"session_id": session_id},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
