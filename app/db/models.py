"""
SQLAlchemy ORM models for database entities.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserModel(Base):
    """
    Application user model for JWT authentication.
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship(
        "SessionModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email}>"


class ProductModel(Base):
    """
    Product catalog model for ecommerce-style inventory.
    """

    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    orders = relationship(
        "OrderModel",
        back_populates="product",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<ProductModel id={self.id} name={self.name}>"


class SessionModel(Base):
    """
    Chat session model.
    Represents a conversation session between a user and the chatbot.
    """

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship(
        "UserModel",
        back_populates="sessions",
    )
    messages = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<SessionModel id={self.id}>"


class OrderModel(Base):
    """
    Order model representing a purchase of a single product.
    """

    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    shipping_address = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(String(50), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship(
        "ProductModel",
        back_populates="orders",
    )

    __table_args__ = (
        Index("ix_orders_created_at", "created_at"),
        Index("ix_orders_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<OrderModel id={self.id} status={self.status}>"


class MessageModel(Base):
    """
    Message model.
    Represents a single message in a conversation.
    """

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship(
        "SessionModel",
        back_populates="messages",
    )

    # Indexes
    __table_args__ = (
        Index("ix_messages_session_id", "session_id"),
        Index("ix_messages_created_at", "created_at"),
        Index("ix_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<MessageModel id={self.id} role={self.role}>"
