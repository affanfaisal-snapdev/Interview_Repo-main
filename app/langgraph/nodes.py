"""
LangGraph nodes for the chat workflow.

Each node represents a step in the conversation workflow.
"""

from typing import Any
import asyncio

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.services.gemini_client import GeminiClient, Message
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatNodes:
    """
    Collection of nodes for the chat graph workflow.
    """

    def __init__(self, gemini_client: GeminiClient = None):
        self.gemini_client = gemini_client or GeminiClient()

    def call_gemini_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Node that calls the Gemini API.

        This node:
        1. Extracts message history from state
        2. Calls Gemini API
        3. Adds response to state

        Args:
            state: Current graph state

        Returns:
            Updated state with Gemini response
        """
        logger.info("Executing call_gemini_node")

        messages = state.get("messages", [])
        if not messages:
            logger.error("No messages in state")
            return state

        # Convert messages to Message objects for Gemini client
        # Handle both dict and LangChain message objects
        gemini_messages = []
        for msg in messages:
            if isinstance(msg, BaseMessage):
                # LangChain message object
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                content = msg.content
            elif isinstance(msg, dict):
                # Dictionary message
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                logger.warning(f"Unknown message type: {type(msg)}")
                continue
                
            gemini_messages.append(
                Message(
                    role=role,
                    content=content,
                )
            )

        # Call Gemini API synchronously (will be wrapped for async in service)
        try:
            response_text = asyncio.run(
                self.gemini_client.generate_response(
                    messages=gemini_messages,
                    system_instruction="You are a helpful AI assistant. Provide clear, accurate, and concise responses.",
                )
            )

            # Add assistant response to messages as AIMessage for LangGraph
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=response_text))

            logger.info("Successfully called Gemini API")
            return {"messages": messages}

        except Exception as e:
            logger.error(f"Error calling Gemini: {str(e)}")
            # Return error message
            from langchain_core.messages import AIMessage
            messages.append(
                AIMessage(content="I encountered an error processing your request. Please try again.")
            )
            return {"messages": messages}

    def process_input_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Node that processes and validates input.

        Args:
            state: Current graph state

        Returns:
            Updated state
        """
        logger.info("Executing process_input_node")

        messages = state.get("messages", [])

        # Validate that we have messages
        if not messages:
            logger.warning("No messages to process")
            return state

        # Basic validation - handle both dict and LangChain message objects
        for msg in messages:
            if isinstance(msg, BaseMessage):
                # LangChain message object - these are always valid
                continue
            elif isinstance(msg, dict):
                if "role" not in msg or "content" not in msg:
                    logger.warning(f"Invalid message structure: {msg}")

        logger.debug(f"Processing {len(messages)} messages")
        return state

    def format_output_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Node that formats the final output.

        Args:
            state: Current graph state

        Returns:
            Formatted state
        """
        logger.info("Executing format_output_node")

        messages = state.get("messages", [])

        # Messages are already properly formatted by LangGraph's MessagesState
        # No need to modify LangChain message objects
        logger.debug(f"Formatted {len(messages)} messages")
        return {"messages": messages}
