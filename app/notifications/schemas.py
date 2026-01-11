"""
Pydantic schemas for notifications API.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    """
    Single notification response.
    
    Used in:
    - GET /notifications (list of these)
    - POST /notifications/{id}/read (returns updated notification)
    """
    id: int
    user_id: int
    type: str
    message: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationsListResponse(BaseModel):
    """
    Response for GET /notifications.
    
    UX Purpose:
    Shows notification feed with unread count badge.
    Client can display red badge with unread_count on notifications icon.
    """
    notifications: list[NotificationResponse]
    total: int = Field(description="Total number of notifications")
    unread_count: int = Field(description="Number of unread notifications")


class MarkReadResponse(BaseModel):
    """
    Response for marking notification(s) as read.
    """
    success: bool
    marked_count: int = Field(description="Number of notifications marked as read")
