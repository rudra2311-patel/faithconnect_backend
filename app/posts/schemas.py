"""
Schemas for leader post creation.
"""

from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, Literal


class CreatePostRequest(BaseModel):
    """Request schema for creating a post."""
    content_text: str = Field(..., min_length=1, max_length=5000, description="Post content")
    media_url: Optional[str] = Field(None, description="URL to image or video")
    media_type: Optional[Literal["image", "video"]] = Field(None, description="Type of media")
    tag: Literal["PRAYER", "WISDOM", "MOTIVATION", "MEDITATION", "COMMUNITY", "TEACHING"] = Field(
        "WISDOM", 
        description="Content category tag"
    )
    intent: Literal["COMFORT", "GUIDANCE", "MOTIVATION", "PRAYER", "TEACHING"] = Field(
        "GUIDANCE",
        description="Message purpose/intent"
    )
    scheduled_at: Optional[datetime] = Field(None, description="Schedule post for future (UTC)")
    
    @model_validator(mode='after')
    def validate_media_fields(self):
        """Ensure media_type is provided if media_url is set."""
        if self.media_url and not self.media_type:
            raise ValueError("media_type is required when media_url is provided")
        if self.media_type and not self.media_url:
            raise ValueError("media_url is required when media_type is provided")
        return self


class PostResponse(BaseModel):
    """Response schema for a created/retrieved post."""
    id: int
    leader_id: int
    content_text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    tag: str
    intent: str
    scheduled_at: Optional[datetime] = None
    is_published: bool
    is_active: bool
    created_at: datetime
    
    # PART 2: Preview and status fields
    is_preview: bool = False  # UX: Indicates this is a preview, not saved to database
    status: Optional[Literal["published", "scheduled"]] = None  # UX: Clear status for leader content management
    
    class Config:
        from_attributes = True


class LeaderPostsResponse(BaseModel):
    """Response schema for leader's posts list."""
    posts: list[PostResponse]
    total: int


class PostPreviewResponse(BaseModel):
    """Response schema for post preview (not saved to database)."""
    post: PostResponse
    message: str = "Preview generated - not saved to database"


class LeaderInfo(BaseModel):
    """Leader information for preview responses."""
    id: int
    name: str
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    
    class Config:
        from_attributes = True
