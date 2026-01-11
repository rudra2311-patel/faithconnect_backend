"""
Schemas for comment operations.

Request/response models for commenting on posts.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CommentRequest(BaseModel):
    """
    Request body for adding a comment to a post.
    
    UX: Simple text field for sharing thoughts or reflections.
    Example: "This prayer really spoke to me today. Thank you for sharing."
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Comment text (1-1000 characters)"
    )
    
    @validator("text")
    def validate_text(cls, v):
        """Ensure comment is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Comment text cannot be empty")
        return v.strip()


class UserInfo(BaseModel):
    """
    Basic user information for comment display.
    
    UX: Shows who wrote the comment with their profile photo.
    """
    id: int
    name: str
    profile_photo: Optional[str]
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """
    Full comment data with user info.
    
    Used to display comments under posts in the feed.
    """
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime
    user: UserInfo  # Includes user name and profile photo
    
    class Config:
        from_attributes = True


class CommentsResponse(BaseModel):
    """
    List of comments for a post.
    
    UX: Displays all comments in chronological order (oldest first)
    to maintain natural conversation flow.
    """
    comments: list[CommentResponse] = Field(
        default_factory=list,
        description="Comments ordered by oldest first"
    )
    total: int = Field(
        description="Total number of comments"
    )
