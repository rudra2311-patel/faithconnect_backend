"""
Engagement models for post likes and saves.

Real-world use case:
Worshipers interact with spiritual content by liking or saving posts.
- Likes express appreciation/agreement
- Saves bookmark content for later reflection or prayer

These actions help worshipers curate their spiritual journey and
provide feedback to leaders about impactful content.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class PostLike(Base):
    """
    Represents a worshiper liking a post.
    
    Design principles:
    - One user can only like a post once (unique constraint)
    - Idempotent: liking again does nothing
    - Soft feedback mechanism for leaders
    
    UX: Heart icon that toggles on/off
    """
    __tablename__ = "post_likes"
    
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    post = relationship("Post", backref="likes")
    user = relationship("User")
    
    # Unique constraint ensures one like per user per post
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_like'),
    )


class PostSave(Base):
    """
    Represents a worshiper saving a post for later.
    
    Design principles:
    - One user can only save a post once (unique constraint)
    - Idempotent: saving again does nothing
    - Personal bookmarking system
    
    UX: Bookmark icon that toggles on/off
    Future: GET /worshipers/me/saved-posts endpoint
    """
    __tablename__ = "post_saves"
    
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    post = relationship("Post", backref="saves")
    user = relationship("User")
    
    # Unique constraint ensures one save per user per post
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_save'),
    )
