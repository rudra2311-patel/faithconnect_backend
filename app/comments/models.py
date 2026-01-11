"""
Comment model for post discussions.

Real-world use case:
Users can leave comments on spiritual posts to share their thoughts,
ask questions, or engage with the community. Comments create dialogue
around spiritual content and foster connection.

Design: Simple flat comments (no replies, no editing, no deletion).
This keeps the feature focused on meaningful initial reactions rather
than complex threaded discussions.
"""

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Comment(Base):
    """
    Represents a comment on a post.
    
    Workflow:
    1. User reads a post and wants to share their thoughts
    2. User writes a comment
    3. Comment is saved and displayed under the post
    4. Comments are ordered oldest first (chronological discussion)
    
    No editing or deletion to keep conversations authentic and simple.
    """
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships for easy access to related data
    post = relationship("Post", backref="comments")
    user = relationship("User")
