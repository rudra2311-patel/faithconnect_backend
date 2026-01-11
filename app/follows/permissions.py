from fastapi import HTTPException, status
from app.auth.models import User, UserRole


def require_worshiper(current_user: User) -> User:
    """
    Ensure the current user is a worshiper.
    
    Raises:
        HTTPException: If user is not a worshiper
    """
    if current_user.role != UserRole.WORSHIPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only worshipers can perform this action"
        )
    return current_user


def require_leader(current_user: User) -> User:
    """
    Ensure the current user is a leader.
    
    Raises:
        HTTPException: If user is not a leader
    """
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can perform this action"
        )
    return current_user
