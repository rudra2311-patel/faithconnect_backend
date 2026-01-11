"""
Business logic for post engagement (likes and saves).

Handles idempotent like/save operations and engagement stats computation.
"""

from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from typing import Dict, Optional

from app.engagement.models import PostLike, PostSave
from app.feed.models import Post
from app.comments.models import Comment


def like_post(db: Session, post_id: int, user_id: int) -> str:
    """
    Like a post (idempotent).
    
    Real-world use case:
    Worshiper reads a prayer post that resonates deeply.
    They tap the heart icon to express appreciation.
    
    If already liked → does nothing (idempotent)
    If not liked → creates like record
    
    Returns:
        str: Success message
    """
    # Check if already liked
    query = select(PostLike).where(
        and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
    )
    result = db.execute(query)
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        return "Post already liked"
    
    # Create new like
    new_like = PostLike(post_id=post_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    
    return "Post liked"


def unlike_post(db: Session, post_id: int, user_id: int) -> str:
    """
    Unlike a post (idempotent).
    
    Real-world use case:
    Worshiper accidentally liked a post or changed their mind.
    They tap the heart icon again to remove the like.
    
    If liked → removes like record
    If not liked → does nothing (idempotent)
    
    Returns:
        str: Success message
    """
    # Find and delete like
    query = select(PostLike).where(
        and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
    )
    result = db.execute(query)
    existing_like = result.scalar_one_or_none()
    
    if not existing_like:
        return "Post not liked"
    
    db.delete(existing_like)
    db.commit()
    
    return "Post unliked"


def save_post(db: Session, post_id: int, user_id: int) -> str:
    """
    Save a post for later (idempotent).
    
    Real-world use case:
    Worshiper finds a meditation guide they want to revisit.
    They tap the bookmark icon to save it for later reflection.
    
    If already saved → does nothing (idempotent)
    If not saved → creates save record
    
    Returns:
        str: Success message
    """
    # Check if already saved
    query = select(PostSave).where(
        and_(PostSave.post_id == post_id, PostSave.user_id == user_id)
    )
    result = db.execute(query)
    existing_save = result.scalar_one_or_none()
    
    if existing_save:
        return "Post already saved"
    
    # Create new save
    new_save = PostSave(post_id=post_id, user_id=user_id)
    db.add(new_save)
    db.commit()
    
    return "Post saved"


def unsave_post(db: Session, post_id: int, user_id: int) -> str:
    """
    Unsave a post (idempotent).
    
    Real-world use case:
    Worshiper has many saved posts and wants to clean up their bookmarks.
    They tap the bookmark icon again to remove it from saved items.
    
    If saved → removes save record
    If not saved → does nothing (idempotent)
    
    Returns:
        str: Success message
    """
    # Find and delete save
    query = select(PostSave).where(
        and_(PostSave.post_id == post_id, PostSave.user_id == user_id)
    )
    result = db.execute(query)
    existing_save = result.scalar_one_or_none()
    
    if not existing_save:
        return "Post not saved"
    
    db.delete(existing_save)
    db.commit()
    
    return "Post unsaved"


def get_post_engagement_stats(
    db: Session,
    post_id: int,
    user_id: Optional[int] = None
) -> Dict:
    """
    Get engagement stats for a post.
    
    Computes:
    - likes_count: Total number of likes
    - comments_count: Total number of comments
    - is_liked: Whether current user liked (if user_id provided)
    - is_saved: Whether current user saved (if user_id provided)
    
    Used by feed services to add engagement data to posts.
    
    Args:
        db: Database session
        post_id: The post to get stats for
        user_id: Current user (optional, for is_liked/is_saved)
        
    Returns:
        Dict with likes_count, comments_count, is_liked, is_saved
    """
    # Get likes count
    likes_query = select(func.count(PostLike.user_id)).where(
        PostLike.post_id == post_id
    )
    likes_count = db.execute(likes_query).scalar() or 0
    
    # Get comments count
    comments_query = select(func.count(Comment.id)).where(
        Comment.post_id == post_id
    )
    comments_count = db.execute(comments_query).scalar() or 0
    
    # Check if user liked (if user_id provided)
    is_liked = False
    if user_id:
        like_query = select(PostLike).where(
            and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
        )
        is_liked = db.execute(like_query).scalar_one_or_none() is not None
    
    # Check if user saved (if user_id provided)
    is_saved = False
    if user_id:
        save_query = select(PostSave).where(
            and_(PostSave.post_id == post_id, PostSave.user_id == user_id)
        )
        is_saved = db.execute(save_query).scalar_one_or_none() is not None
    
    return {
        "likes_count": likes_count,
        "comments_count": comments_count,
        "is_liked": is_liked,
        "is_saved": is_saved
    }
