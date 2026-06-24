"""
Chat service - orchestrates conversation logic.
"""

from typing import List
from sqlalchemy.orm import Session

from app.db.session import SessionRepository, MessageRepository
from app.schemas.message import MessageData
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """
    Service for chat operations.
    Handles session validation, message storage, and conversation history.
    """

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)

    def validate_session(self, session_id: str) -> bool:
        """
        Validate that a session exists.

        Args:
            session_id: Session UUID

        Returns:
            True if session exists, False otherwise
        """
        exists = self.session_repo.session_exists(session_id)
        if not exists:
            logger.warning(f"Session not found: {session_id}")
        return exists

    def store_user_message(self, session_id: str, message: str) -> MessageData:
        """
        Store a user message in the database.

        Args:
            session_id: Session UUID
            message: Message text

        Returns:
            MessageData object
        """
        msg_model = self.message_repo.create_message(
            session_id=session_id,
            role="user",
            content=message,
        )
        return self._model_to_schema(msg_model)

    def store_assistant_message(
        self, session_id: str, message: str
    ) -> MessageData:
        """
        Store an assistant message in the database.

        Args:
            session_id: Session UUID
            message: Message text

        Returns:
            MessageData object
        """
        msg_model = self.message_repo.create_message(
            session_id=session_id,
            role="assistant",
            content=message,
        )
        return self._model_to_schema(msg_model)

    def get_conversation_history(self, session_id: str) -> List[MessageData]:
        """
        Get the full conversation history for a session.

        Args:
            session_id: Session UUID

        Returns:
            List of MessageData objects in chronological order
        """
        messages = self.message_repo.get_session_messages(session_id)
        return [self._model_to_schema(msg) for msg in messages]

    def get_message_count(self, session_id: str) -> int:
        """
        Get the total number of messages in a session.

        Args:
            session_id: Session UUID

        Returns:
            Message count
        """
        return self.message_repo.get_session_message_count(session_id)

    @staticmethod
    def _model_to_schema(msg_model) -> MessageData:
        """
        Convert MessageModel to MessageData schema.

        Args:
            msg_model: MessageModel instance

        Returns:
            MessageData instance
        """
        return MessageData(
            role=msg_model.role,
            content=msg_model.content,
            created_at=msg_model.created_at,
        )
