"""
LangGraph graph definition for the chat workflow.
"""

from typing import Any

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState

from app.chatgraph.nodes import ChatNodes
from app.services.gemini_client import GeminiClient
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_SQL_REPAIR_ATTEMPTS = 3


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
        route: str
        db: Any
        sql_query: str
        sql_error: str
        repair_attempts: int

    return ChatState


def create_chat_graph():
    """
    Create and compile the chat workflow graph.

    Returns:
        Compiled LangGraph StateGraph
    """
    logger.info("Creating chat workflow graph")

    # Initialize nodes
    gemini_client = GeminiClient()
    nodes = ChatNodes(gemini_client=gemini_client)

    # Create graph
    graph_builder = StateGraph(create_chat_state())

    # Add nodes
    graph_builder.add_node("process_input", nodes.process_input_node)
    graph_builder.add_node("classify_intent", nodes.classify_intent_node)
    graph_builder.add_node("generate_sql", nodes.generate_sql_node)
    graph_builder.add_node("validate_execute_sql", nodes.validate_execute_sql_node)
    graph_builder.add_node("repair_sql", nodes.repair_sql_node)
    graph_builder.add_node("call_gemini", nodes.call_gemini_node)
    graph_builder.add_node("format_output", nodes.format_output_node)

    # Add edges
    graph_builder.add_edge(START, "process_input")
    graph_builder.add_edge("process_input", "classify_intent")
    graph_builder.add_conditional_edges(
        "classify_intent",
        lambda state: state.get("route", "general_chat"),
        {
            "ecommerce_query": "generate_sql",
            "general_chat": "call_gemini",
        },
    )
    graph_builder.add_conditional_edges(
        "generate_sql",
        lambda state: "call_gemini" if state.get("sql_query") == "UNSUPPORTED" else "validate_execute_sql",
        {
            "call_gemini": "call_gemini",
            "validate_execute_sql": "validate_execute_sql",
        },
    )
    graph_builder.add_conditional_edges(
        "validate_execute_sql",
        lambda state: (
            "repair_sql"
            if state.get("sql_error")
            and state.get("repair_attempts", 0) < MAX_SQL_REPAIR_ATTEMPTS
            else "call_gemini" if state.get("sql_error") else "format_output"
        ),
        {
            "repair_sql": "repair_sql",
            "call_gemini": "call_gemini",
            "format_output": "format_output",
        },
    )
    graph_builder.add_edge("repair_sql", "validate_execute_sql")
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
    except Exception:
        pass

    return (
        "Graph Flow:\n"
        "START -> process_input -> classify_intent -> "
        "[generate_sql -> validate_execute_sql -> repair_sql?] or [call_gemini] -> format_output -> END"
    )
