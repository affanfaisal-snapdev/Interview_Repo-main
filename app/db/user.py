"""
Database repository for user authentication operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import UserModel

logger = get_logger(__name__)


class UserRepository:
    """
    Repository for user database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password_hash: str) -> UserModel:
        """
        Create a new user record.
        """
        user = UserModel(email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Created user: {user.email}")
        return user

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """
        Fetch a user by email address.
        """
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """
        Fetch a user by primary key.
        """
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
