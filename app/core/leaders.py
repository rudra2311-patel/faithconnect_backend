"""
Leaders discovery endpoint.

Provides endpoints for discovering and exploring leaders.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole
from app.follows.schemas import LeaderProfileResponse
from app.follows.services import get_all_leaders_with_follow_status, is_following
from app.follows.permissions import require_worshiper
from app.follows.models import Follow
from app.feed.models import Post

router = APIRouter(tags=["Leaders"])


@router.get("/leaders", response_model=List[LeaderProfileResponse])
def get_all_leaders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all leaders with follow status for the current worshiper.
    
    Used in the Explore Leaders / Discover screen where worshipers
    can browse and follow spiritual leaders.
    
    Returns a list of all leaders with their profiles and whether
    the current worshiper is following them.
    
    Requirements:
    - Current user must be a worshiper
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Get all leaders with follow status
    results = get_all_leaders_with_follow_status(db, current_user.id)
    
    # Transform to response format
    leaders = []
    for user, is_following in results:
        leaders.append(LeaderProfileResponse(
            leader_id=user.id,
            name=user.name,
            faith=user.faith,
            profile_photo=user.profile_photo,
            bio=user.bio,
            is_following=is_following
        ))
    
    return leaders


@router.get("/leaders/{leader_id}", response_model=LeaderProfileResponse)
def get_leader_profile(
    leader_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific leader's profile.
    
    Used when viewing an individual leader's profile page.
    Returns leader info with follow status for the current worshiper.
    
    Parameters:
    - leader_id: The user ID of the leader (users.id where role=LEADER)
    
    Requirements:
    - Current user must be a worshiper
    
    Returns:
    - Leader profile with follow status
    
    Raises:
    - 404: Leader not found or user is not a leader
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Get leader user from database
    leader = db.query(User).filter(
        User.id == leader_id,
        User.role == UserRole.LEADER
    ).first()
    
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leader with ID {leader_id} not found"
        )
    
    # Check if current worshiper is following this leader
    following = is_following(db, current_user.id, leader_id)
    
    # Count followers for this leader
    followers_count = db.query(func.count(Follow.id)).filter(
        Follow.leader_id == leader_id
    ).scalar() or 0
    
    # Count published posts for this leader
    posts_count = db.query(func.count(Post.id)).filter(
        Post.leader_id == leader_id,
        Post.is_published == True
    ).scalar() or 0
    
    return LeaderProfileResponse(
        leader_id=leader.id,
        name=leader.name,
        faith=leader.faith,
        profile_photo=leader.profile_photo,
        bio=leader.bio,
        is_following=following,
        followers_count=followers_count,
        posts_count=posts_count
    )
