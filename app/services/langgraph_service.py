"""
LangGraph service - orchestrates the conversation graph and workflow.
"""

from typing import List
import asyncio

from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.orm import Session
from app.chatgraph.workflow import create_chat_graph
from app.services.gemini_client import GeminiClientError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LangGraphService:
    """
    Service for LangGraph workflow orchestration.
    """

    def __init__(self):
        self.graph = create_chat_graph()

    async def execute_chat(
        self,
        conversation_history: List[dict],
        user_message: str,
        db: Session,
    ) -> str:
        """
        Execute the chat workflow using LangGraph.

        Args:
            conversation_history: List of previous messages with role and content
            user_message: Current user message

        Returns:
            Assistant response text

        Raises:
            GeminiClientError: If upstream Gemini execution fails
            RuntimeError: If workflow execution fails for another reason
        """
        logger.info("Executing LangGraph chat workflow")

        try:
            # Convert conversation history to LangChain message objects
            langchain_messages = []
            for msg in conversation_history:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                else:
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            # Add current user message
            langchain_messages.append(HumanMessage(content=user_message))
            
            # Build the state for the graph
            state = {
                "messages": langchain_messages,
                "db": db,
                "repair_attempts": 0,
                "route": "general_chat",
                "sql_query": "",
                "sql_error": "",
            }

            logger.debug(f"Initial state with {len(langchain_messages)} messages")

            # Execute the graph
            # Note: LangGraph invoke is sync, but we can use asyncio if needed
            result = await asyncio.to_thread(self.graph.invoke, state)

            logger.debug(f"Graph result with {len(result.get('messages', []))} messages")

            # Extract the last message (assistant response)
            if "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                # Handle both dict and LangChain message objects
                if isinstance(last_message, AIMessage):
                    response_text = last_message.content
                    logger.info("LangGraph workflow completed successfully")
                    return response_text
                elif isinstance(last_message, dict) and last_message.get("role") == "assistant":
                    response_text = last_message.get("content", "")
                    logger.info("LangGraph workflow completed successfully")
                    return response_text

            raise RuntimeError("No assistant response in graph output")

        except GeminiClientError:
            raise
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {str(e)}")
            raise RuntimeError(f"Workflow execution failed: {str(e)}") from e

    def get_graph_info(self) -> dict:
        """
        Get information about the graph structure.

        Returns:
            Dictionary with graph metadata
        """
        return {
            "nodes": list(self.graph.nodes.keys()) if hasattr(self.graph, "nodes") else [],
            "description": "LangGraph chat workflow for Gemini integration",
        }
