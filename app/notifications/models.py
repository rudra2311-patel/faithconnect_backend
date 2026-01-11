"""
SQLAlchemy models for in-app notifications.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Notification(Base):
    """
    In-app notification model.
    
    Business Rules:
    - Notifications are created synchronously (no background workers)
    - Notifications are never deleted, only marked as read
    - Reference type and ID allow linking back to source (post, chat, question)
    
    UX Purpose:
    Users see a notification feed showing recent activity relevant to them:
    - Leaders see new followers and question answers they provided
    - Worshipers see new posts, message replies, and answers to their questions
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification type (e.g., "new_follower", "new_post", "new_message")
    type = Column(String(50), nullable=False, index=True)
    
    # Human-readable message shown in notification feed
    message = Column(Text, nullable=False)
    
    # Reference to source entity (post, chat, question, etc.)
    reference_type = Column(String(20), nullable=True)  # "post", "chat", "question"
    reference_id = Column(Integer, nullable=True)
    
    # Read status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
