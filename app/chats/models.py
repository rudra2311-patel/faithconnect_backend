"""
Chat and Message models for private messaging.

Real-world use case:
Worshipers and leaders engage in private conversations for spiritual
guidance, prayer requests, or personal questions. This is asynchronous
messaging (not real-time chat) to support thoughtful dialogue.

Design principles:
- One chat per worshiper-leader pair (unique constraint)
- Messages are immutable (no editing/deletion)
- Sender role is stored for clear attribution
- Chronological ordering for natural conversation flow
- Unread tracking for notification system
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.base import Base


class SenderRole(str, Enum):
    """Role of message sender for clear attribution."""
    WORSHIPER = "worshiper"
    LEADER = "leader"


class Chat(Base):
    """
    Represents a conversation between a worshiper and a leader.
    
    Design:
    - One chat per worshiper-leader pair (enforced by unique constraint)
    - Chat persists across multiple conversations
    - Both participants can send messages
    
    Workflow:
    1. Worshiper initiates chat by sending first message to a leader
    2. Chat is created automatically if it doesn't exist
    3. Leader receives message and can respond
    4. Conversation continues asynchronously
    """
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    worshiper_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    leader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    worshiper = relationship("User", foreign_keys=[worshiper_id])
    leader = relationship("User", foreign_keys=[leader_id])
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    
    # Unique constraint: one chat per worshiper-leader pair
    __table_args__ = (
        UniqueConstraint('worshiper_id', 'leader_id', name='uq_chat_participants'),
    )


class Message(Base):
    """
    Represents a single message in a chat.
    
    Design:
    - Immutable (no editing or deletion)
    - Sender role stored explicitly for clarity
    - Chronologically ordered
    - Tracks read status for notifications
    
    Faith-aligned async messaging:
    Messages are designed for thoughtful spiritual guidance, not rapid
    back-and-forth. Leaders can take time to craft meaningful responses.
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(SQLEnum(SenderRole), nullable=False)
    content_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Read tracking for notifications
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")
