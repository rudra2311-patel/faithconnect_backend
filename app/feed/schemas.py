from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LeaderInfo(BaseModel):
    """Leader information for feed posts."""
    id: int
    name: str
    bio: Optional[str] = None
    profile_photo: Optional[str] = None

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Response schema for a single post in feed."""
    id: int
    leader: LeaderInfo
    content_text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    created_at: datetime
    
    # Engagement metrics (placeholder values for PART 1)
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    is_saved: bool = False
    
    # PART 2: Feed metadata extras for enhanced UX
    is_daily_reflection: bool = False  # UX: Highlights one post for focused spiritual practice
    content_tone: Optional[str] = None  # UX: Helps frontend apply mode-specific styling (inspiration/guidance/community)
    time_context: Optional[str] = None  # UX: Enables time-aware messaging (morning prayer, evening reflection)
    is_new: bool = False  # UX: Visual badge for fresh content to drive engagement
    feed_reason: Optional[str] = None  # UX: Shows users why they're seeing this post (explore vs following)
    
    # PART 4: Contextual feed moments (refinement)
    moment_label: Optional[str] = None  # UX: Enables journey-based grouping (Morning Reflection, Midday Guidance, Evening Thought)

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    """Paginated feed response."""
    posts: list[PostResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DailyReflectionResponse(BaseModel):
    """Response for daily reflection endpoint."""
    date: str  # YYYY-MM-DD format
    post: Optional[PostResponse] = None
    message: str
