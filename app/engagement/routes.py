"""
Routes for post engagement (likes and saves).

Enables worshipers to interact with spiritual content.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole
from app.engagement.schemas import EngagementResponse
from app.engagement.services import like_post, unlike_post, save_post, unsave_post
from app.feed.models import Post


router = APIRouter(tags=["Engagement"])


def require_worshiper(current_user: User) -> None:
    """
    Enforce worshiper-only access for engagement actions.
    
    Business rule: Only worshipers can like/save posts.
    Leaders create content; worshipers engage with it.
    
    Raises:
        HTTPException 403: If user is not a worshiper
    """
    if current_user.role != UserRole.WORSHIPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only worshipers can like or save posts"
        )


def verify_post_exists(db: Session, post_id: int) -> None:
    """
    Verify that a post exists before allowing engagement.
    
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


@router.post("/posts/{post_id}/like", response_model=EngagementResponse)
def like_a_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a post.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 for leaders).
    
    Real-world use case:
    Worshiper reads a powerful prayer or teaching that resonates
    with them. They tap the heart icon to express appreciation
    and provide feedback to the leader.
    
    Idempotent behavior:
    - If not yet liked → creates like (201)
    - If already liked → returns success message (200)
    
    UX: Heart icon fills with color when liked.
    Leaders can see total likes_count on their posts.
    """
    # Role enforcement
    require_worshiper(current_user)
    
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Like the post (idempotent)
    message = like_post(db=db, post_id=post_id, user_id=current_user.id)
    
    return EngagementResponse(message=message)


@router.delete("/posts/{post_id}/like", response_model=EngagementResponse)
def unlike_a_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike a post.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 for leaders).
    
    Real-world use case:
    Worshiper accidentally liked a post or changed their mind.
    They tap the heart icon again to remove the like.
    
    Idempotent behavior:
    - If currently liked → removes like (200)
    - If not liked → returns success message (200)
    
    UX: Heart icon returns to outline when unliked.
    """
    # Role enforcement
    require_worshiper(current_user)
    
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Unlike the post (idempotent)
    message = unlike_post(db=db, post_id=post_id, user_id=current_user.id)
    
    return EngagementResponse(message=message)


@router.post("/posts/{post_id}/save", response_model=EngagementResponse)
def save_a_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a post for later.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 for leaders).
    
    Real-world use case:
    Worshiper finds a meditation guide or teaching they want to
    revisit during their personal prayer time. They tap the
    bookmark icon to save it for later reflection.
    
    Idempotent behavior:
    - If not yet saved → creates save (201)
    - If already saved → returns success message (200)
    
    UX: Bookmark icon fills with color when saved.
    Future: GET /worshipers/me/saved-posts to view all saved content.
    """
    # Role enforcement
    require_worshiper(current_user)
    
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Save the post (idempotent)
    message = save_post(db=db, post_id=post_id, user_id=current_user.id)
    
    return EngagementResponse(message=message)


@router.delete("/posts/{post_id}/save", response_model=EngagementResponse)
def unsave_a_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unsave a post.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 for leaders).
    
    Real-world use case:
    Worshiper has many saved posts and wants to clean up their
    bookmarks. They tap the bookmark icon again to remove it
    from their saved collection.
    
    Idempotent behavior:
    - If currently saved → removes save (200)
    - If not saved → returns success message (200)
    
    UX: Bookmark icon returns to outline when unsaved.
    """
    # Role enforcement
    require_worshiper(current_user)
    
    # Verify post exists
    verify_post_exists(db, post_id)
    
    # Unsave the post (idempotent)
    message = unsave_post(db=db, post_id=post_id, user_id=current_user.id)
    
    return EngagementResponse(message=message)
