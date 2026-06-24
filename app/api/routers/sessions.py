"""
API routers for session management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.session import SessionRepository
from app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionInfoResponse,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
    responses={
        201: {"description": "Session created successfully"},
        500: {"description": "Internal server error"},
    },
)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
) -> SessionCreateResponse:
    """
    Create a new chat session.

    Returns:
        - session_id: UUID of the new session
        - created_at: Timestamp of creation

    Example:
        POST /api/v1/sessions
        Response:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2026-02-12T10:00:00"
        }
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.create_session()

        logger.info(f"Created new session: {session.id}")

        return SessionCreateResponse(
            session_id=session.id,
            created_at=session.created_at,
        )
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        )


@router.get(
    "/{session_id}",
    response_model=SessionInfoResponse,
    summary="Get session information",
    responses={
        200: {"description": "Session information retrieved"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionInfoResponse:
    """
    Get information about a specific session.

    Args:
        session_id: UUID of the session

    Returns:
        - session_id: Session UUID
        - created_at: Session creation timestamp
        - message_count: Total messages in session

    Example:
        GET /api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
        Response:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2026-02-12T10:00:00",
            "message_count": 5
        }
    """
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_session(session_id)

        if not session:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        # Get message count
        from app.db.session import MessageRepository

        msg_repo = MessageRepository(db)
        message_count = msg_repo.get_session_message_count(session_id)

        return SessionInfoResponse(
            session_id=session.id,
            created_at=session.created_at,
            message_count=message_count,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session",
        )
