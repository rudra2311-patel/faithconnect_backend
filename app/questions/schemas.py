"""
Schemas for question operations.

Request/response models for worshiper-leader Q&A feature.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class AskQuestionRequest(BaseModel):
    """
    Request body for worshiper asking a question to a leader.
    
    UX: Simple text field where worshiper types their question.
    Example: "How do I maintain faith during difficult times?"
    """
    question_text: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The question text (10-1000 characters)"
    )
    
    @validator("question_text")
    def validate_question_text(cls, v):
        """Ensure question is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Question text cannot be empty")
        return v.strip()


class AnswerQuestionRequest(BaseModel):
    """
    Request body for leader answering a question.
    
    UX: Text field for leader's thoughtful response.
    Example: "Faith during trials is strengthened through prayer..."
    """
    answer_text: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The answer text (10-2000 characters)"
    )
    
    @validator("answer_text")
    def validate_answer_text(cls, v):
        """Ensure answer is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Answer text cannot be empty")
        return v.strip()


class WorshiperInfo(BaseModel):
    """
    Basic worshiper information for leader's inbox.
    
    UX: Shows who asked the question without exposing too much info.
    """
    id: int
    name: str
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    """
    Full question data with worshiper info.
    
    Used in leader's inbox to display questions with context about who asked.
    """
    id: int
    worshiper_id: int
    leader_id: int
    question_text: str
    answer_text: Optional[str]
    answered: bool
    created_at: datetime
    answered_at: Optional[datetime]
    worshiper: WorshiperInfo  # Includes worshiper name for context
    
    class Config:
        from_attributes = True


class LeaderQuestionsResponse(BaseModel):
    """
    Leader's question inbox organized by status.
    
    UX: Two sections in the inbox:
    1. Pending - questions waiting for response (prioritize these)
    2. Answered - questions already responded to (archive/history)
    
    This helps leaders triage their inbox and see what needs attention.
    """
    pending: list[QuestionResponse] = Field(
        default_factory=list,
        description="Questions not yet answered (answered = false)"
    )
    answered: list[QuestionResponse] = Field(
        default_factory=list,
        description="Questions already answered (answered = true)"
    )
    total_pending: int = Field(
        description="Count of unanswered questions"
    )
    total_answered: int = Field(
        description="Count of answered questions"
    )
