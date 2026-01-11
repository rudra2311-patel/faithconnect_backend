"""
Business logic for notifications.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.notifications.models import Notification
from typing import Optional


def create_notification(
    db: Session,
    user_id: int,
    type: str,
    message: str,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None
) -> Notification:
    """
    Create a new notification.
    
    Called synchronously when events occur (no background workers).
    
    Args:
        db: Database session
        user_id: User to notify
        type: Notification type (e.g., "new_follower", "new_post")
        message: Human-readable message
        reference_type: Optional entity type ("post", "chat", "question")
        reference_id: Optional entity ID
    
    Returns:
        Created notification
    
    UX Purpose:
    Notifications appear in user's feed immediately after action occurs.
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        reference_type=reference_type,
        reference_id=reference_id,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    limit: int = 50,
    include_read: bool = True
) -> tuple[list[Notification], int]:
    """
    Get user's notifications ordered by newest first.
    
    Args:
        db: Database session
        user_id: User ID
        limit: Maximum notifications to return
        include_read: Whether to include read notifications
    
    Returns:
        Tuple of (notifications list, unread_count)
    
    UX Purpose:
    Shows notification feed with most recent items first.
    Unread count shown as badge on notifications icon.
    """
    # Build query
    stmt = select(Notification).where(Notification.user_id == user_id)
    
    if not include_read:
        stmt = stmt.where(Notification.is_read == False)
    
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
    
    # Execute query
    result = db.execute(stmt)
    notifications = result.scalars().all()
    
    # Get unread count
    unread_stmt = select(Notification).where(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    unread_result = db.execute(unread_stmt)
    unread_count = len(unread_result.scalars().all())
    
    return notifications, unread_count


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """
    Mark a notification as read.
    
    Args:
        db: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)
    
    Returns:
        Updated notification or None if not found/unauthorized
    
    UX Purpose:
    When user taps notification, it's marked as read and badge count decreases.
    """
    stmt = select(Notification).where(
        and_(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    )
    result = db.execute(stmt)
    notification = result.scalar_one_or_none()
    
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    
    return notification


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """
    Mark all user's notifications as read.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Number of notifications marked as read
    
    UX Purpose:
    "Mark all as read" button clears notification badge.
    """
    stmt = select(Notification).where(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    result = db.execute(stmt)
    notifications = result.scalars().all()
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        count += 1
    
    db.commit()
    return count
