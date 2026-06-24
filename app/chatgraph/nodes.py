"""
LangGraph nodes for the chat workflow.

Each node represents a step in the conversation workflow.
"""

from typing import Any
import asyncio

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from sqlalchemy.orm import Session

from app.services.gemini_client import GeminiClient, GeminiClientError, Message
from app.services.nl_to_sql import NLToSQLService
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

        except GeminiClientError as e:
            logger.error(f"Error calling Gemini: {str(e)}")
            raise

    def classify_intent_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Route likely ecommerce data questions into the NL-to-SQL branch.
        """
        logger.info("Executing classify_intent_node")
        user_message = self._get_latest_user_message(state)
        route = "ecommerce_query" if NLToSQLService.is_ecommerce_query(user_message) else "general_chat"
        return {"route": route}

    def generate_sql_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Generate SQL for products/orders questions.
        """
        logger.info("Executing generate_sql_node")
        db = self._get_db_session(state)
        user_message = self._get_latest_user_message(state)
        service = NLToSQLService(db=db, gemini_client=self.gemini_client)
        sql_query = asyncio.run(service.generate_sql(user_message))
        return {"sql_query": sql_query}

    def validate_execute_sql_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and execute the generated SQL.
        """
        logger.info("Executing validate_execute_sql_node")
        db = self._get_db_session(state)
        sql_query = state.get("sql_query", "")
        service = NLToSQLService(db=db, gemini_client=self.gemini_client)

        if sql_query == "UNSUPPORTED":
            return {"route": "general_chat", "sql_error": "", "sql_query": ""}

        try:
            validated_sql = service.validate_sql(sql_query)
            rows = service.execute_sql(validated_sql)
            response_text = service.format_response(rows)
            messages = list(state.get("messages", []))
            messages.append(AIMessage(content=response_text))
            return {"messages": messages, "sql_error": ""}
        except ValueError as exc:
            logger.warning("SQL validation/execution failed: %s", exc)
            return {"sql_error": str(exc)}

    def repair_sql_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Repair a failed SQL query once using the model.
        """
        logger.info("Executing repair_sql_node")
        db = self._get_db_session(state)
        user_message = self._get_latest_user_message(state)
        sql_query = state.get("sql_query", "")
        sql_error = state.get("sql_error", "")
        repair_attempts = state.get("repair_attempts", 0) + 1
        service = NLToSQLService(db=db, gemini_client=self.gemini_client)
        repaired_sql = asyncio.run(service.repair_sql(user_message, sql_query, sql_error))
        return {"sql_query": repaired_sql, "repair_attempts": repair_attempts, "sql_error": ""}

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

    @staticmethod
    def _get_latest_user_message(state: dict[str, Any]) -> str:
        messages = state.get("messages", [])
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
            if isinstance(message, dict) and message.get("role") == "user":
                return message.get("content", "")
        return ""

    @staticmethod
    def _get_db_session(state: dict[str, Any]) -> Session:
        db = state.get("db")
        if db is None:
            raise RuntimeError("Database session missing from graph state")
        return db
