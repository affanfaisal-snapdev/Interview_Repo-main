"""
Database session utilities.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import SessionModel, MessageModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class SessionRepository:
    """
    Repository for session database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: str) -> SessionModel:
        """
        Create a new chat session.

        Returns:
            Created SessionModel
        """
        session = SessionModel(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info(f"Created session: {session.id}")
        return session

    def get_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[SessionModel]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session UUID

        Returns:
            SessionModel or None if not found
        """
        query = self.db.query(SessionModel).filter(SessionModel.id == session_id)
        if user_id is not None:
            query = query.filter(SessionModel.user_id == user_id)
        return query.first()

    def session_exists(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """
        Check if a session exists.

        Args:
            session_id: Session UUID

        Returns:
            True if session exists, False otherwise
        """
        query = self.db.query(SessionModel).filter(SessionModel.id == session_id)
        if user_id is not None:
            query = query.filter(SessionModel.user_id == user_id)
        return query.count() > 0


class MessageRepository:
    """
    Repository for message database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self, session_id: str, role: str, content: str
    ) -> MessageModel:
        """
        Create a new message.

        Args:
            session_id: Session UUID
            role: Message role ("user" or "assistant")
            content: Message text content

        Returns:
            Created MessageModel
        """
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        logger.info(f"Created message: {message.id} for session: {session_id}")
        return message

    def get_session_messages(self, session_id: str) -> list[MessageModel]:
        """
        Retrieve all messages for a session in chronological order.

        Args:
            session_id: Session UUID

        Returns:
            List of MessageModel ordered by creation time
        """
        return (
            self.db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
            .all()
        )

    def get_session_message_count(self, session_id: str) -> int:
        """
        Get total message count for a session.

        Args:
            session_id: Session UUID

        Returns:
            Message count
        """
        return (
            self.db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .count()
        )
