"""
LangGraph graph definition for the chat workflow.

Uses the latest LangGraph syntax with StateGraph and MessagesState.
"""

from typing import Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState

from app.langgraph.nodes import ChatNodes
from app.services.gemini_client import GeminiClient
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_chat_state() -> type:
    """
    Define the state schema for the chat graph.

    Returns:
        State class
    """
    class ChatState(MessagesState):
        """
        Extended MessagesState for our chat workflow.
        """
        pass

    return ChatState


def create_chat_graph():
    """
    Create and compile the chat workflow graph.

    The graph follows this flow:
    1. START -> process_input (validate input)
    2. process_input -> call_gemini (call Gemini API)
    3. call_gemini -> format_output (format response)
    4. format_output -> END

    Returns:
        Compiled LangGraph StateGraph
    """
    logger.info("Creating chat workflow graph")

    # Initialize nodes
    gemini_client = GeminiClient()
    nodes = ChatNodes(gemini_client=gemini_client)

    # Create graph
    graph_builder = StateGraph(MessagesState)

    # Add nodes
    graph_builder.add_node("process_input", nodes.process_input_node)
    graph_builder.add_node("call_gemini", nodes.call_gemini_node)
    graph_builder.add_node("format_output", nodes.format_output_node)

    # Add edges
    graph_builder.add_edge(START, "process_input")
    graph_builder.add_edge("process_input", "call_gemini")
    graph_builder.add_edge("call_gemini", "format_output")
    graph_builder.add_edge("format_output", END)

    # Compile graph
    graph = graph_builder.compile()

    logger.info("Chat workflow graph created and compiled successfully")

    return graph


def get_graph_visualization() -> str:
    """
    Get ASCII visualization of the graph structure.

    Returns:
        ASCII art representation of the graph
    """
    graph = create_chat_graph()

    # Try to get Mermaid representation if available
    try:
        if hasattr(graph, "get_graph"):
            return graph.get_graph().draw_ascii()
    except:
        pass

    return (
        "Graph Flow:\n"
        "START -> process_input -> call_gemini -> format_output -> END"
    )
