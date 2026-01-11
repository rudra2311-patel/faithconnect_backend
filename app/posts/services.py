"""
Services for leader post creation.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timezone
from app.feed.models import Post, PostTag, PostIntent, MediaType
from app.posts.schemas import CreatePostRequest, PostResponse
from app.auth.models import User
from typing import List, Dict


def create_post(
    db: Session,
    leader_id: int,
    post_data: CreatePostRequest
) -> Post:
    """
    Create a new post for a leader.
    
    Leader Experience:
    - If scheduled_at is null or in the past → post is immediately published
    - If scheduled_at is in the future → post is saved but not published yet
    - This allows leaders to prepare content in advance and schedule for optimal times
    
    No background jobs needed - feed queries filter by is_published automatically.
    """
    # Determine if post should be published immediately
    now = datetime.now(timezone.utc)
    should_publish = True
    
    if post_data.scheduled_at:
        # Make scheduled_at timezone-aware if naive
        scheduled_time = post_data.scheduled_at
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
        
        # If scheduled for future, don't publish yet
        if scheduled_time > now:
            should_publish = False
    
    # Convert media_type string to enum
    media_type_enum = None
    if post_data.media_type:
        media_type_enum = MediaType[post_data.media_type.upper()]
    
    # Create post
    new_post = Post(
        leader_id=leader_id,
        content_text=post_data.content_text,
        media_url=post_data.media_url,
        media_type=media_type_enum,
        tag=PostTag[post_data.tag],
        intent=PostIntent[post_data.intent],
        scheduled_at=post_data.scheduled_at,
        is_published=should_publish,
        is_active=True
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # UX: If post is published immediately, notify all followers
    # This keeps worshipers engaged with fresh spiritual content
    if should_publish:
        from app.notifications.services import create_notification
        from app.follows.models import Follow
        
        # Get leader info for notification message
        leader = db.query(User).filter(User.id == leader_id).first()
        
        # Get all followers of this leader
        followers = db.query(Follow).filter(Follow.leader_id == leader_id).all()
        
        # Create notification for each follower
        for follow in followers:
            create_notification(
                db=db,
                user_id=follow.worshiper_id,
                type="new_post",
                message=f"{leader.name} shared new spiritual content",
                reference_type="post",
                reference_id=new_post.id
            )
    
    return new_post


def get_leader_posts(
    db: Session,
    leader_id: int
) -> List[Post]:
    """
    Get all posts created by a leader.
    
    Includes both published and scheduled posts.
    Leaders need to see their full content pipeline.
    Ordered by newest first (created_at desc).
    """
    query = (
        select(Post)
        .where(Post.leader_id == leader_id)
        .where(Post.is_active == True)
        .order_by(Post.created_at.desc())
    )
    
    result = db.execute(query)
    return result.scalars().all()


def preview_post(
    leader: User,
    post_data: CreatePostRequest
) -> Dict:
    """
    Generate a preview of a post without saving to database.
    
    Leader Experience: Allows leaders to see exactly how their post will appear
    in feeds before publishing. Builds confidence and reduces editing cycles.
    
    UX Benefits:
    - Preview formatting, tags, and intent before committing
    - Check how content will appear to followers
    - No database writes - safe to experiment
    
    Returns a feed-style post object with is_preview=True.
    """
    now = datetime.now(timezone.utc)
    
    # Determine if post would be published immediately
    should_publish = True
    if post_data.scheduled_at:
        scheduled_time = post_data.scheduled_at
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
        if scheduled_time > now:
            should_publish = False
    
    # Build preview response (no database ID, using 0 as placeholder)
    preview_response = PostResponse(
        id=0,  # Placeholder - not saved to database
        leader_id=leader.id,
        content_text=post_data.content_text,
        media_url=post_data.media_url,
        media_type=post_data.media_type,
        tag=post_data.tag,
        intent=post_data.intent,
        scheduled_at=post_data.scheduled_at,
        is_published=should_publish,
        is_active=True,
        created_at=now,
        is_preview=True,  # Mark as preview
        status="published" if should_publish else "scheduled"
    )
    
    return {
        "post": preview_response,
        "message": "Preview generated - not saved to database"
    }


def compute_post_status(post: Post) -> str:
    """
    Compute display status for a post.
    
    UX Purpose: Provides clear status visibility for leaders managing
    their content pipeline.
    
    Returns:
    - "published" if is_published is True
    - "scheduled" if is_published is False
    """
    return "published" if post.is_published else "scheduled"
