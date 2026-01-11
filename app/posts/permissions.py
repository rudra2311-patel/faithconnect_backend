"""
Permission helpers for post operations.
"""

from fastapi import HTTPException, status
from app.auth.models import User, UserRole


def require_leader(current_user: User) -> None:
    """
    Ensure the current user is a leader.
    
    Raises HTTP 403 if not a leader.
    Only leaders can create posts.
    """
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can create posts. Worshipers can follow leaders and view their content."
        )
