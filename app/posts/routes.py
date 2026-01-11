"""
Routes for leader post creation.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.posts.permissions import require_leader
from app.posts.services import create_post, get_leader_posts, preview_post, compute_post_status
from app.posts.schemas import CreatePostRequest, PostResponse, LeaderPostsResponse, PostPreviewResponse


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_leader_post(
    post_data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post as a leader.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    
    Leaders can:
    - Write spiritual content with text and optional media
    - Categorize posts with tags (PRAYER, WISDOM, etc.)
    - Set intent (COMFORT, GUIDANCE, etc.) to clarify message purpose
    - Schedule posts for future publishing (optional)
    
    Publishing Logic:
    - If scheduled_at is null or <= now → post published immediately
    - If scheduled_at > now → post saved as draft, published later
    
    Published posts automatically appear in:
    - Explore feed (all users)
    - Following feed (for followers)
    - Leader profile
    """
    # Role enforcement: raise HTTP 403 if not leader
    require_leader(current_user)
    
    # Create the post
    post = create_post(db=db, leader_id=current_user.id, post_data=post_data)
    
    return post


@router.get("/leaders/me/posts", response_model=LeaderPostsResponse)
def get_my_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all posts created by the authenticated leader.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    
    Returns:
    - All published posts
    - All scheduled posts (not yet published)
    - Ordered by newest first
    
    Leaders need full visibility of their content pipeline to manage
    their spiritual messaging effectively.
    """
    # Role enforcement: raise HTTP 403 if not leader
    require_leader(current_user)
    
    # Get all posts by this leader
    posts = get_leader_posts(db=db, leader_id=current_user.id)
    
    # Add computed status field to each post
    posts_with_status = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "leader_id": post.leader_id,
            "content_text": post.content_text,
            "media_url": post.media_url,
            "media_type": post.media_type,
            "tag": post.tag,
            "intent": post.intent,
            "scheduled_at": post.scheduled_at,
            "is_published": post.is_published,
            "is_active": post.is_active,
            "created_at": post.created_at,
            "status": compute_post_status(post)
        }
        posts_with_status.append(PostResponse(**post_dict))
    
    return LeaderPostsResponse(
        posts=posts_with_status,
        total=len(posts_with_status)
    )


@router.post("/preview", response_model=PostPreviewResponse)
def preview_leader_post(
    post_data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview a post before publishing.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    
    UX Purpose:
    - Leaders can see exactly how their post will appear in feeds
    - Validates all fields (tags, intent, scheduling)
    - No database writes - safe to experiment
    - Builds confidence before final publish
    
    Returns:
    - Feed-style post object with is_preview=true
    - Leader info (name, faith, profile photo)
    - Status message confirming no save occurred
    
    Workflow:
    1. Leader drafts post content
    2. Calls /posts/preview to see formatted result
    3. Adjusts content/tags/scheduling as needed
    4. Calls POST /posts when ready to publish
    """
    # Role enforcement: raise HTTP 403 if not leader
    require_leader(current_user)
    
    # Generate preview without database save
    preview_data = preview_post(leader=current_user, post_data=post_data)
    
    return preview_data
