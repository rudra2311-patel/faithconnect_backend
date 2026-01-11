from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class MediaType(str, enum.Enum):
    """Media type enumeration for posts."""
    IMAGE = "image"
    VIDEO = "video"


class PostTag(str, enum.Enum):
    """Post tag for categorizing spiritual content."""
    PRAYER = "PRAYER"
    WISDOM = "WISDOM"
    MOTIVATION = "MOTIVATION"
    MEDITATION = "MEDITATION"
    COMMUNITY = "COMMUNITY"
    TEACHING = "TEACHING"


class PostIntent(str, enum.Enum):
    """Post intent to clarify the purpose of the spiritual message."""
    COMFORT = "COMFORT"
    GUIDANCE = "GUIDANCE"
    MOTIVATION = "MOTIVATION"
    PRAYER = "PRAYER"
    TEACHING = "TEACHING"


class Post(Base):
    """
    Post model for leader content.
    
    Only leaders can create posts.
    Posts are consumed by worshipers in their feed.
    
    Leader Experience:
    - tag: Helps leaders categorize their spiritual content (prayer, wisdom, etc.)
    - intent: Clarifies the purpose of the message (comfort, guidance, etc.)
    - scheduled_at: Allows leaders to schedule posts in advance for optimal timing
    - is_published: Controls visibility - scheduled posts remain hidden until time arrives
    """
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_text = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    media_type = Column(SQLEnum(MediaType), nullable=True)
    
    # Leader post creation fields
    tag = Column(SQLEnum(PostTag), default=PostTag.WISDOM, nullable=False)
    intent = Column(SQLEnum(PostIntent), default=PostIntent.GUIDANCE, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    is_published = Column(Boolean, default=True, nullable=False, index=True)
    
    # Soft delete and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<Post(id={self.id}, leader_id={self.leader_id}, is_published={self.is_published})>"
