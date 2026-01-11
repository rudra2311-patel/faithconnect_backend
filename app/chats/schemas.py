"""
Schemas for chat operations.

Request/response models for messaging between worshipers and leaders.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class SendMessageRequest(BaseModel):
    """
    Request body for sending a message.
    
    UX: Simple text field for typing message.
    Example: "I've been struggling with faith lately and need guidance."
    """
    content_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Message text (1-2000 characters)"
    )
    
    @validator("content_text")
    def validate_content_text(cls, v):
        """Ensure message is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Message text cannot be empty")
        return v.strip()


class UserInfo(BaseModel):
    """
    Basic user information for message display.
    
    UX: Shows who sent the message with their profile photo.
    """
    id: int
    name: str
    profile_photo: Optional[str]
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """
    Full message data with sender info.
    
    Used to display messages in chat view.
    """
    id: int
    chat_id: int
    sender_id: int
    sender_role: str  # "worshiper" or "leader"
    content_text: str
    created_at: datetime
    is_read: bool = False
    read_at: Optional[datetime] = None
    sender: UserInfo  # Includes sender name and profile photo
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """
    Full chat data with all messages.
    
    UX: Chat view showing conversation between worshiper and leader.
    Messages ordered chronologically (oldest first) for natural flow.
    """
    id: int
    worshiper_id: int
    leader_id: int
    created_at: datetime
    worshiper: UserInfo
    leader: UserInfo
    messages: list[MessageResponse] = Field(
        default_factory=list,
        description="Messages ordered by oldest first"
    )
    
    class Config:
        from_attributes = True


class ChatSummary(BaseModel):
    """
    Chat summary for inbox view.
    
    UX: Shows list of chats with participant info and last message preview.
    Used by leaders to see their inbox and by worshipers to see their conversations.
    Includes unread count for notification badges.
    """
    id: int
    worshiper_id: int
    leader_id: int
    created_at: datetime
    worshiper: UserInfo
    leader: UserInfo
    last_message: Optional[MessageResponse] = Field(
        None,
        description="Most recent message in the chat"
    )
    unread_count: int = Field(
        default=0,
        description="Number of unread messages for current user"
    )
    
    class Config:
        from_attributes = True


class ChatsListResponse(BaseModel):
    """
    List of chats for inbox view.
    
    UX: Inbox showing all conversations.
    For leaders: all worshipers who've messaged them
    For worshipers: all leaders they've messaged
    """
    chats: list[ChatSummary] = Field(
        default_factory=list,
        description="Chats ordered by most recent message"
    )
    total: int = Field(
        description="Total number of chats"
    )
