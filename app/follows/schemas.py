from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ==================== Response Schemas ====================

class FollowResponse(BaseModel):
    """Generic success response for follow/unfollow actions."""
    message: str


class LeaderProfileResponse(BaseModel):
    """Leader profile with follow status."""
    leader_id: int
    name: str
    faith: Optional[str] = None
    profile_photo: Optional[str] = None
    bio: Optional[str] = None
    is_following: bool
    followers_count: int = 0
    posts_count: int = 0

    class Config:
        from_attributes = True


class FollowerResponse(BaseModel):
    """Worshiper follower info."""
    worshiper_id: int
    name: str
    profile_photo: Optional[str] = None
    followed_at: datetime

    class Config:
        from_attributes = True


class FollowStatusResponse(BaseModel):
    """Response for checking if following a leader."""
    is_following: bool
