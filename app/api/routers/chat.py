"""
API routers for chat endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.message import ChatRequest, ChatResponse
from app.services.chat import ChatService
from app.services.langgraph_service import LangGraphService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize LangGraph service (singleton-like)
langgraph_service = LangGraphService()


@router.post(
    "/message",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message in a chat session",
    responses={
        200: {"description": "Message processed successfully"},
        404: {"description": "Session not found"},
        422: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Send a message in an existing chat session.

    The flow:
    1. Validate session exists
    2. Store user message
    3. Load conversation history
    4. Execute LangGraph workflow (calls Gemini API)
    5. Store assistant response
    6. Return full conversation

    Args:
        chat_request: Contains session_id and message text

    Returns:
        - session_id: Session UUID
        - user_message: User's input
        - assistant_message: AI assistant's response
        - conversation_history: Full conversation history

    Example:
        POST /api/v1/chat/message
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "message": "What is the capital of France?"
        }

        Response:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_message": "What is the capital of France?",
            "assistant_message": "The capital of France is Paris.",
            "conversation_history": [...]
        }
    """
    try:
        # Initialize services
        chat_service = ChatService(db)

        # Validate session exists
        if not chat_service.validate_session(chat_request.session_id):
            logger.warning(f"Invalid session: {chat_request.session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        logger.info(f"Processing message for session: {chat_request.session_id}")

        # Store user message
        user_msg_data = chat_service.store_user_message(
            session_id=chat_request.session_id,
            message=chat_request.message,
        )

        # Get conversation history before the current message (for context)
        conversation_history = [
            msg.dict() for msg in chat_service.get_conversation_history(chat_request.session_id)
        ]

        # Remove the message we just added (we'll add it back as part of the workflow)
        if conversation_history and conversation_history[-1]["content"] == chat_request.message:
            conversation_history = conversation_history[:-1]

        # Execute LangGraph workflow
        logger.info("Starting LangGraph workflow")
        assistant_response = await langgraph_service.execute_chat(
            conversation_history=conversation_history,
            user_message=chat_request.message,
        )

        # Store assistant response
        assistant_msg_data = chat_service.store_assistant_message(
            session_id=chat_request.session_id,
            message=assistant_response,
        )

        # Get full conversation history
        full_history = chat_service.get_conversation_history(chat_request.session_id)

        logger.info(f"Chat completed for session: {chat_request.session_id}")

        return ChatResponse(
            session_id=chat_request.session_id,
            user_message=chat_request.message,
            assistant_message=assistant_response,
            conversation_history=full_history,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )
