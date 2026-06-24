"""
Quick start guide for running the chatbot application.

This script demonstrates basic usage patterns.
"""

import asyncio
import requests
from typing import Optional


BASE_URL = "http://localhost:8000/api/v1"


def create_session() -> str:
    """Create a new chat session."""
    response = requests.post(f"{BASE_URL}/sessions")
    response.raise_for_status()
    data = response.json()
    session_id = data["session_id"]
    print(f"✅ Created session: {session_id}")
    return session_id


def send_message(session_id: str, message: str) -> dict:
    """Send a message in a chat session."""
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={
            "session_id": session_id,
            "message": message,
        },
    )
    response.raise_for_status()
    return response.json()


def get_session_info(session_id: str) -> dict:
    """Get session information."""
    response = requests.get(f"{BASE_URL}/sessions/{session_id}")
    response.raise_for_status()
    return response.json()


def check_health() -> dict:
    """Check application health."""
    response = requests.get("http://localhost:8000/health")
    response.raise_for_status()
    return response.json()


def main():
    """Run interactive chatbot session."""
    print("🤖 AI Chatbot Backend - Interactive Demo")
    print("=" * 50)
    print()

    # Check health
    try:
        health = check_health()
        print(f"✅ Server healthy: {health}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("   Make sure to run: uvicorn app.main:app --reload")
        return

    print()

    # Create session
    try:
        session_id = create_session()
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        return

    print()

    # Get session info
    try:
        info = get_session_info(session_id)
        print(f"📊 Session info: {info}")
    except Exception as e:
        print(f"❌ Failed to get session info: {e}")

    print()
    print("💬 Chat Interface")
    print("=" * 50)
    print("Type 'exit' to quit")
    print()

    # Interactive chat loop
    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                print("👋 Goodbye!")
                break

            if not user_input:
                continue

            print("\n⏳ Waiting for response...")

            response = send_message(session_id, user_input)

            print(f"\n🤖 Assistant: {response['assistant_message']}")
            print(f"\n📈 Total messages: {len(response['conversation_history'])}")
            print("-" * 50)
            print()

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
