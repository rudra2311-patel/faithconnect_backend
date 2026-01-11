"""
Routes for post comments.

Enables users to comment on spiritual posts and view comments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.comments.schemas import CommentRequest, CommentResponse, CommentsResponse
from app.comments.services import add_comment, get_comments
from app.feed.models import Post


router = APIRouter(tags=["Comments"])


def verify_post_exists(db: Session, post_id: int) -> None:
    """
    Verify that a post exists before allowing comments.
    
    Raises:
        HTTPException 404: If post doesn't exist
    """
    query = select(Post).where(Post.id == post_id)
    result = db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def add_comment_to_post(
    post_id: int,
    comment_data: CommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a post.
    
    Role Enforcement: ALL AUTHENTICATED USERS (worshipers and leaders).
    
    Real-world use case:
    User reads a spiritual post that resonates with them.
    They want to share their thoughts, ask a question, or express gratitude.
    Comments create dialogue around spiritual content.
    
    Design principles:
    - Simple flat comments (no replies)
    - No editing or deletion (authentic conversations)
    - Everyone can comment (both worshipers and leaders)
    
    UX: Text field under each post for quick reactions.
    """
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Add the comment
    comment = add_comment(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
        comment_data=comment_data
    )
    
    return comment


@router.get("/posts/{post_id}/comments", response_model=CommentsResponse)
def get_post_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a post.
    
    Role Enforcement: ALL AUTHENTICATED USERS (worshipers and leaders).
    
    Real-world use case:
    User opens a post and wants to see what others have said.
    Comments appear in chronological order (oldest first) to show
    natural conversation flow.
    
    Returns:
    - List of comments with user info (name, profile photo)
    - Total comment count
    - Ordered oldest first (chronological)
    
    UX: Comments section under post showing community engagement.
    """
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Get all comments for this post
    comments = get_comments(db=db, post_id=post_id)
    
    return CommentsResponse(
        comments=comments,
        total=len(comments)
    )
