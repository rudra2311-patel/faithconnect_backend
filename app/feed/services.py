from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.feed.models import Post
from app.auth.models import User
from app.follows.models import Follow
from app.feed.schemas import PostResponse, LeaderInfo, FeedResponse
from app.engagement.services import get_post_engagement_stats
from typing import List, Optional, Literal
from datetime import datetime, timezone, timedelta


def _compute_content_tone(post: Post, mode: Optional[str] = None) -> str:
    """
    Compute content tone for contextual feed mode support.
    
    UX Purpose: Allows frontend to apply mode-specific styling and filtering.
    Simple heuristic: video=inspiration, long text=guidance, default=community
    """
    if mode and mode in ["inspiration", "guidance", "community"]:
        return mode
    
    # Dummy mapping when no mode specified
    if post.media_type and post.media_type.value == "video":
        return "inspiration"
    elif len(post.content_text) > 500:
        return "guidance"
    else:
        return "community"


def _compute_time_context(created_at: datetime) -> str:
    """
    Compute time context for faith moments / micro-journey.
    
    UX Purpose: Enables time-aware messaging like "Start your day with this prayer"
    or "Evening reflection time".
    """
    hour = created_at.hour
    
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "evening"


def _is_new_content(created_at: datetime) -> bool:
    """
    Check if content is new (within last 24 hours).
    
    UX Purpose: Visual badge to highlight fresh content and drive engagement.
    """
    now = datetime.now(timezone.utc)
    # Make created_at timezone-aware if it's naive
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    return (now - created_at) < timedelta(hours=24)


def _get_moment_label(time_context: str) -> str:
    """
    Map time context to a human-friendly moment label.
    
    UX Purpose: Enables frontend to group posts into journey-based moments,
    creating a calmer, narrative-driven feed experience rather than an
    overwhelming chronological stream.
    """
    mapping = {
        "morning": "Morning Reflection",
        "afternoon": "Midday Guidance",
        "evening": "Evening Thought"
    }
    return mapping.get(time_context, "Daily Moment")


def get_explore_feed(
    db: Session,
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    mode: Optional[str] = None
) -> FeedResponse:
    """
    Get all posts from all active leaders, ordered by newest first.
    
    Available to all authenticated users (worshipers and leaders).
    Uses JOIN to fetch leader info in one query (no N+1).
    
    UX Purpose: Provides discovery of all spiritual content from active leaders,
    helping users explore the full community without algorithmic filtering.
    """
    # Pagination hardening: clamp page_size to maximum of 50
    page_size = min(page_size, 50)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count of active, published posts
    total_query = select(func.count(Post.id)).where(
        Post.is_active == True
    ).where(
        Post.is_published == True
    )
    total = db.execute(total_query).scalar_one()
    
    # Get posts with leader info using JOIN
    query = (
        select(Post, User)
        .join(User, Post.leader_id == User.id)
        .where(Post.is_active == True)
        .where(Post.is_published == True)
        .where(User.is_active == True)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    results = db.execute(query).all()
    
    # Build response objects
    posts = []
    for idx, (post, leader) in enumerate(results):
        leader_info = LeaderInfo(
            id=leader.id,
            name=leader.name,
            bio=leader.bio,
            profile_photo=leader.profile_photo
        )
        
        # PART 2: Compute metadata extras
        # Daily reflection: Mark the first post as daily reflection (deterministic)
        is_daily_reflection = (idx == 0 and page == 1)
        
        # PART 2 & 4: Compute metadata extras
        time_ctx = _compute_time_context(post.created_at)
        
        # PART 4A & 4B: Get engagement stats dynamically
        engagement_stats = get_post_engagement_stats(db, post.id, user_id)
        
        post_response = PostResponse(
            id=post.id,
            leader=leader_info,
            content_text=post.content_text,
            media_url=post.media_url,
            media_type=post.media_type.value if post.media_type else None,
            created_at=post.created_at,
            # PART 4A & 4B: Engagement metrics computed dynamically
            likes_count=engagement_stats["likes_count"],
            comments_count=engagement_stats["comments_count"],
            is_liked=engagement_stats["is_liked"],
            is_saved=engagement_stats["is_saved"],
            # PART 2: Metadata fields
            is_daily_reflection=is_daily_reflection,
            content_tone=_compute_content_tone(post, mode),
            time_context=time_ctx,
            is_new=_is_new_content(post.created_at),
            feed_reason="explore",  # Explicitly set: user is browsing explore feed
            # PART 4: Moment label
            moment_label=_get_moment_label(time_ctx)
        )
        posts.append(post_response)
    
    # Pagination hardening: correct has_more calculation
    has_more = total > (page * page_size)
    
    # Empty state safety: if no posts, return empty list (not error)
    return FeedResponse(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


def get_following_feed(
    db: Session,
    worshiper_id: int,
    page: int = 1,
    page_size: int = 10,
    mode: Optional[str] = None
) -> FeedResponse:
    """
    Get posts from leaders that the worshiper follows, ordered by newest first.
    
    Only available to worshipers (role enforcement in routes layer).
    Uses JOINs to fetch posts and leader info efficiently (no N+1).
    
    UX Purpose: Provides a personalized feed of content from leaders the worshiper
    has chosen to follow, creating a curated spiritual experience.
    """
    # Pagination hardening: clamp page_size to maximum of 50
    page_size = min(page_size, 50)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count of posts from followed leaders
    total_query = (
        select(func.count(Post.id))
        .join(Follow, Post.leader_id == Follow.leader_id)
        .where(Follow.worshiper_id == worshiper_id)
        .where(Post.is_active == True)
        .where(Post.is_published == True)
    )
    total = db.execute(total_query).scalar_one()
    
    # Get posts with leader info using JOINs
    query = (
        select(Post, User)
        .join(Follow, Post.leader_id == Follow.leader_id)
        .join(User, Post.leader_id == User.id)
        .where(Follow.worshiper_id == worshiper_id)
        .where(Post.is_active == True)
        .where(Post.is_published == True)
        .where(User.is_active == True)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    results = db.execute(query).all()
    
    # Build response objects
    posts = []
    for idx, (post, leader) in enumerate(results):
        leader_info = LeaderInfo(
            id=leader.id,
            name=leader.name,
            bio=leader.bio,
            profile_photo=leader.profile_photo
        )
        
        # PART 2: Compute metadata extras
        # Daily reflection: Mark the first post as daily reflection (deterministic)
        is_daily_reflection = (idx == 0 and page == 1)
        
        # PART 2 & 4: Compute metadata extras
        time_ctx = _compute_time_context(post.created_at)
        
        # PART 4A & 4B: Get engagement stats dynamically
        engagement_stats = get_post_engagement_stats(db, post.id, worshiper_id)
        
        post_response = PostResponse(
            id=post.id,
            leader=leader_info,
            content_text=post.content_text,
            media_url=post.media_url,
            media_type=post.media_type.value if post.media_type else None,
            created_at=post.created_at,
            # PART 4A & 4B: Engagement metrics computed dynamically
            likes_count=engagement_stats["likes_count"],
            comments_count=engagement_stats["comments_count"],
            is_liked=engagement_stats["is_liked"],
            is_saved=engagement_stats["is_saved"],
            # PART 2: Metadata fields
            is_daily_reflection=is_daily_reflection,
            content_tone=_compute_content_tone(post, mode),
            time_context=time_ctx,
            is_new=_is_new_content(post.created_at),
            feed_reason="following",  # Explicitly set: user is viewing their following feed
            # PART 4: Moment label
            moment_label=_get_moment_label(time_ctx)
        )
        posts.append(post_response)
    
    # Pagination hardening: correct has_more calculation
    has_more = total > (page * page_size)
    
    # Empty state safety: if worshiper follows no leaders or they have no posts, return empty list
    return FeedResponse(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


def get_daily_reflection(
    db: Session,
    user_id: Optional[int] = None
) -> dict:
    """
    Get today's guided daily reflection post.
    
    UX Purpose: Provides ONE meaningful piece of content per day for a calm,
    guided spiritual experience. This creates a focused moment rather than
    overwhelming users with a full feed. Supports mindful consumption over
    endless scrolling.
    
    Available to all authenticated users (worshipers and leaders).
    
    Logic: Simple time-based selection - latest post from last 24 hours.
    No persistence, no tracking, no recommendation algorithm.
    Gracefully handles empty state with null post.
    """
    from datetime import date
    
    # Get current date for response
    today = date.today().isoformat()
    
    # Calculate 24 hours ago
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Query for the latest post within last 24 hours
    query = (
        select(Post, User)
        .join(User, Post.leader_id == User.id)
        .where(Post.is_active == True)
        .where(Post.is_published == True)
        .where(User.is_active == True)
        .where(Post.created_at >= twenty_four_hours_ago)
        .order_by(Post.created_at.desc())
        .limit(1)
    )
    
    result = db.execute(query).first()
    
    # If no post found, return null post with appropriate message
    if not result:
        return {
            "date": today,
            "post": None,
            "message": "No reflection available for today"
        }
    
    post, leader = result
    
    # Build leader info
    leader_info = LeaderInfo(
        id=leader.id,
        name=leader.name,
        bio=leader.bio,
        profile_photo=leader.profile_photo
    )
    
    # Build post response without interaction flags (simplified for reflection)
    time_ctx = _compute_time_context(post.created_at)
    
    # PART 4A & 4B: Get engagement stats dynamically
    engagement_stats = get_post_engagement_stats(db, post.id, user_id)
    
    post_response = PostResponse(
        id=post.id,
        leader=leader_info,
        content_text=post.content_text,
        media_url=post.media_url,
        media_type=post.media_type.value if post.media_type else None,
        created_at=post.created_at,
        # PART 4A & 4B: Engagement metrics computed dynamically
        likes_count=engagement_stats["likes_count"],
        comments_count=engagement_stats["comments_count"],
        is_liked=engagement_stats["is_liked"],
        is_saved=engagement_stats["is_saved"],
        # Metadata fields - CRITICAL: is_daily_reflection MUST be true for this endpoint
        # This endpoint exists ONLY to return the daily reflection post
        is_daily_reflection=True,
        content_tone=_compute_content_tone(post, None),
        time_context=time_ctx,
        is_new=_is_new_content(post.created_at),
        feed_reason="daily_reflection",  # Explicitly set: this is from daily reflection endpoint
        # PART 4: Moment label
        moment_label=_get_moment_label(time_ctx)
    )
    
    return {
        "date": today,
        "post": post_response,
        "message": "Today's Reflection"
    }

