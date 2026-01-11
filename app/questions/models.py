"""
Question model for worshiper-leader Q&A.

Real-world use case:
A worshiper follows a spiritual leader and has a personal question about
faith, prayer, or guidance. They can submit the question privately, and
the leader can respond thoughtfully when they have time.

This supports deeper 1:1 spiritual guidance beyond public posts.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from app.db.base import Base


class Question(Base):
    """
    Represents a question from a worshiper to a leader.
    
    Workflow:
    1. Worshiper submits question → answered = False
    2. Leader views inbox → sees pending questions
    3. Leader responds → answered = True, answered_at set
    4. Worshiper views their asked questions → sees answer
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    worshiper_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    answered = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships for easy access to user data
    worshiper = relationship("User", foreign_keys=[worshiper_id])
    leader = relationship("User", foreign_keys=[leader_id])
