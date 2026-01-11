"""
Business logic for comment operations.

Handles comment creation, retrieval, and counting.
"""

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.comments.models import Comment
from app.comments.schemas import CommentRequest


def add_comment(
    db: Session,
    post_id: int,
    user_id: int,
    comment_data: CommentRequest
) -> Comment:
    """
    Add a comment to a post.
    
    Real-world use case:
    A worshiper reads a spiritual teaching that resonates with them.
    They want to share their reflection or ask a follow-up question.
    Their comment is saved and becomes part of the conversation.
    
    Returns:
        Comment: The newly created comment
    """
    # Create new comment
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        text=comment_data.text
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


def get_comments(
    db: Session,
    post_id: int
) -> list[Comment]:
    """
    Get all comments for a post.
    
    Real-world use case:
    User opens a post and wants to see what others have said.
    Comments are shown in chronological order (oldest first)
    to maintain natural conversation flow.
    
    Returns:
        list[Comment]: Comments ordered by oldest first with user info
    """
    # Get comments with user info using JOIN
    query = select(Comment).where(
        Comment.post_id == post_id
    ).options(
        joinedload(Comment.user)  # Eager load user data
    ).order_by(
        Comment.created_at.asc()  # Oldest first for chronological flow
    )
    
    result = db.execute(query)
    comments = result.scalars().all()
    
    return comments


def get_comments_count(db: Session, post_id: int) -> int:
    """
    Get total number of comments for a post.
    
    Used by feed services to display comment count on posts.
    
    Args:
        db: Database session
        post_id: The post to count comments for
        
    Returns:
        int: Total number of comments
    """
    query = select(func.count(Comment.id)).where(
        Comment.post_id == post_id
    )
    count = db.execute(query).scalar() or 0
    
    return count
