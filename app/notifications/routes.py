"""
API routes for notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.notifications.schemas import (
    NotificationResponse,
    NotificationsListResponse,
    MarkReadResponse
)
from app.notifications.services import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read
)


router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=NotificationsListResponse)
def get_notifications(
    limit: int = Query(50, ge=1, le=100, description="Maximum notifications to return"),
    include_read: bool = Query(True, description="Include read notifications"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's notifications.
    
    Role Enforcement: AUTHENTICATED USERS (all roles).
    
    Real-world use case:
    User opens notification feed to see recent activity:
    - Leaders: See new followers, daily reflection selections
    - Worshipers: See new posts from leaders, message replies, question answers
    
    Returns:
    - List of notifications ordered by newest first
    - Total count
    - Unread count (for badge display)
    
    UX: Notification feed with red badge showing unread count.
    Tapping a notification navigates to the source (post, chat, etc.)
    """
    notifications, unread_count = get_user_notifications(
        db=db,
        user_id=current_user.id,
        limit=limit,
        include_read=include_read
    )
    
    return NotificationsListResponse(
        notifications=notifications,
        total=len(notifications),
        unread_count=unread_count
    )


@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read.
    
    Role Enforcement: AUTHENTICATED USERS (notification owner only).
    
    Real-world use case:
    User taps a notification to view the source content.
    The notification is marked as read and unread badge count decreases.
    
    Returns:
    - Updated notification with is_read=true
    
    UX: Notification changes from bold/highlighted to normal text.
    Badge count on notifications icon decreases by 1.
    """
    notification = mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.post("/notifications/read-all", response_model=MarkReadResponse)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read.
    
    Role Enforcement: AUTHENTICATED USERS (all roles).
    
    Real-world use case:
    User taps "Mark all as read" button to clear notification badge.
    All unread notifications become read at once.
    
    Returns:
    - Success status
    - Number of notifications marked as read
    
    UX: Notification badge disappears (count becomes 0).
    All notifications in feed appear as read.
    """
    marked_count = mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id
    )
    
    return MarkReadResponse(
        success=True,
        marked_count=marked_count
    )
