from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List, Tuple
from app.follows.models import Follow
from app.auth.models import User, UserRole


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Get user by ID or raise 404.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        User object
    
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def validate_leader_exists(db: Session, leader_id: int) -> User:
    """
    Validate that the user exists and is a leader.
    
    Args:
        db: Database session
        leader_id: Leader user ID
    
    Returns:
        Leader user object
    
    Raises:
        HTTPException: If user doesn't exist or is not a leader
    """
    user = get_user_by_id(db, leader_id)
    
    if user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a leader"
        )
    
    return user


def follow_leader(db: Session, worshiper_id: int, leader_id: int) -> Follow:
    """
    Create a follow relationship.
    
    This is idempotent - if the follow already exists, returns existing record.
    
    Args:
        db: Database session
        worshiper_id: Worshiper user ID
        leader_id: Leader user ID
    
    Returns:
        Follow object
    
    Raises:
        HTTPException: If validation fails
    """
    # Validate leader exists and has correct role
    leader = validate_leader_exists(db, leader_id)
    worshiper = get_user_by_id(db, worshiper_id)
    
    # Check if worshiper is trying to follow themselves
    if worshiper_id == leader_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    # Check if follow already exists (idempotent)
    existing_follow = db.query(Follow).filter(
        and_(
            Follow.worshiper_id == worshiper_id,
            Follow.leader_id == leader_id
        )
    ).first()
    
    if existing_follow:
        return existing_follow
    
    # Create new follow
    new_follow = Follow(
        worshiper_id=worshiper_id,
        leader_id=leader_id
    )
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)
    
    # UX: Leader sees notification "[Worshiper Name] started following you"
    # This helps leaders know their community is growing
    from app.notifications.services import create_notification
    create_notification(
        db=db,
        user_id=leader_id,
        type="new_follower",
        message=f"{worshiper.name} started following you",
        reference_type=None,
        reference_id=None
    )
    
    return new_follow


def unfollow_leader(db: Session, worshiper_id: int, leader_id: int) -> bool:
    """
    Remove a follow relationship.
    
    This is idempotent - returns True even if follow didn't exist.
    
    Args:
        db: Database session
        worshiper_id: Worshiper user ID
        leader_id: Leader user ID
    
    Returns:
        True (always, for idempotency)
    """
    follow = db.query(Follow).filter(
        and_(
            Follow.worshiper_id == worshiper_id,
            Follow.leader_id == leader_id
        )
    ).first()
    
    if follow:
        db.delete(follow)
        db.commit()
    
    return True


def get_followed_leaders(db: Session, worshiper_id: int) -> List[Tuple[User, Follow]]:
    """
    Get all leaders followed by a worshiper with follow info.
    
    Args:
        db: Database session
        worshiper_id: Worshiper user ID
    
    Returns:
        List of (User, Follow) tuples
    """
    results = db.query(User, Follow).join(
        Follow, Follow.leader_id == User.id
    ).filter(
        Follow.worshiper_id == worshiper_id
    ).all()
    
    return results


def get_followers(db: Session, leader_id: int) -> List[Tuple[User, Follow]]:
    """
    Get all worshipers following a leader.
    
    Args:
        db: Database session
        leader_id: Leader user ID
    
    Returns:
        List of (User, Follow) tuples
    """
    results = db.query(User, Follow).join(
        Follow, Follow.worshiper_id == User.id
    ).filter(
        Follow.leader_id == leader_id
    ).all()
    
    return results


def is_following(db: Session, worshiper_id: int, leader_id: int) -> bool:
    """
    Check if a worshiper is following a leader.
    
    Args:
        db: Database session
        worshiper_id: Worshiper user ID
        leader_id: Leader user ID
    
    Returns:
        True if following, False otherwise
    """
    follow = db.query(Follow).filter(
        and_(
            Follow.worshiper_id == worshiper_id,
            Follow.leader_id == leader_id
        )
    ).first()
    
    return follow is not None


def get_all_leaders_with_follow_status(
    db: Session,
    worshiper_id: int
) -> List[Tuple[User, bool]]:
    """
    Get all leaders with follow status for a specific worshiper.
    
    Used for the Explore Leaders screen where worshipers can discover
    and follow new leaders.
    
    Args:
        db: Database session
        worshiper_id: Worshiper user ID to check follow status
    
    Returns:
        List of (User, is_following) tuples where User is the leader
        and is_following is a boolean indicating if the worshiper follows them
    """
    # Get all leaders
    leaders = db.query(User).filter(User.role == UserRole.LEADER).all()
    
    print(f"\n[DEBUG] get_all_leaders_with_follow_status:")
    print(f"  Total users in DB: {db.query(User).count()}")
    print(f"  Users with role LEADER: {len(leaders)}")
    print(f"  Users with role WORSHIPER: {db.query(User).filter(User.role == UserRole.WORSHIPER).count()}")
    
    for leader in leaders:
        print(f"    - Leader: ID={leader.id}, Name={leader.name}, Role={leader.role}")
    
    # Get all leader IDs that the worshiper follows
    followed_leader_ids = {
        follow.leader_id
        for follow in db.query(Follow.leader_id).filter(
            Follow.worshiper_id == worshiper_id
        ).all()
    }
    
    # Build result list with follow status
    results = [
        (leader, leader.id in followed_leader_ids)
        for leader in leaders
    ]
    
    return results
