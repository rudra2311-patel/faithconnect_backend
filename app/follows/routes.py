from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.follows.schemas import (
    FollowResponse,
    LeaderProfileResponse,
    FollowerResponse,
    FollowStatusResponse
)
from app.follows.services import (
    follow_leader,
    unfollow_leader,
    get_followed_leaders,
    get_followers,
    is_following,
    get_all_leaders_with_follow_status
)
from app.follows.permissions import require_worshiper, require_leader

router = APIRouter(prefix="/follows", tags=["Follows"])


@router.post("/{leader_id}", response_model=FollowResponse, status_code=status.HTTP_200_OK)
def follow_leader_endpoint(
    leader_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Follow a leader.
    
    - **leader_id**: ID of the leader to follow
    
    Requirements:
    - Current user must be a worshiper
    - Target user must be a leader
    - Idempotent: returns success even if already following
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Create follow relationship
    follow_leader(db, current_user.id, leader_id)
    
    return FollowResponse(message="Leader followed successfully")


@router.delete("/{leader_id}", response_model=FollowResponse, status_code=status.HTTP_200_OK)
def unfollow_leader_endpoint(
    leader_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unfollow a leader.
    
    - **leader_id**: ID of the leader to unfollow
    
    Requirements:
    - Current user must be a worshiper
    - Idempotent: returns success even if not following
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Remove follow relationship
    unfollow_leader(db, current_user.id, leader_id)
    
    return FollowResponse(message="Leader unfollowed successfully")


@router.get("/my-leaders", response_model=List[LeaderProfileResponse])
def get_my_leaders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all leaders followed by the current worshiper.
    
    Returns leader profiles with follow status.
    
    Requirements:
    - Current user must be a worshiper
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Get followed leaders
    results = get_followed_leaders(db, current_user.id)
    
    # Transform to response format
    leaders = []
    for user, follow in results:
        leaders.append(LeaderProfileResponse(
            leader_id=user.id,
            name=user.name,
            faith=user.faith,
            profile_photo=user.profile_photo,
            bio=user.bio,
            is_following=True  # Always true since we're querying followed leaders
        ))
    
    return leaders


@router.get("/my-followers", response_model=List[FollowerResponse])
def get_my_followers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all worshipers following the current leader.
    
    Requirements:
    - Current user must be a leader
    """
    # Enforce leader-only access
    require_leader(current_user)
    
    # Get followers
    results = get_followers(db, current_user.id)
    
    # Transform to response format
    followers = []
    for user, follow in results:
        followers.append(FollowerResponse(
            worshiper_id=user.id,
            name=user.name,
            profile_photo=user.profile_photo,
            followed_at=follow.created_at
        ))
    
    return followers


@router.get("/is-following/{leader_id}", response_model=FollowStatusResponse)
def check_follow_status(
    leader_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current worshiper is following a specific leader.
    
    - **leader_id**: ID of the leader to check
    
    Requirements:
    - Current user must be a worshiper
    """
    # Enforce worshiper-only access
    require_worshiper(current_user)
    
    # Check follow status
    following = is_following(db, current_user.id, leader_id)
    
    return FollowStatusResponse(is_following=following)
