from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.follows.permissions import require_worshiper
from app.feed.services import get_explore_feed, get_following_feed, get_daily_reflection
from app.feed.schemas import FeedResponse, DailyReflectionResponse


router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/explore", response_model=FeedResponse)
def explore_feed(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of posts per page"),
    mode: str = Query(None, description="Feed mode: inspiration, guidance, or community"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all posts from all active leaders.
    
    Role Enforcement: Available to ALL authenticated users (worshipers and leaders).
    No role restrictions - anyone can explore content.
    
    Posts are ordered by newest first.
    Optional mode parameter influences content_tone metadata for frontend styling.
    """
    return get_explore_feed(db=db, user_id=current_user.id, page=page, page_size=page_size, mode=mode)


@router.get("/following", response_model=FeedResponse)
def following_feed(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of posts per page"),
    mode: str = Query(None, description="Feed mode: inspiration, guidance, or community"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get posts from leaders that the worshiper follows.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 if leader tries to access).
    Only worshipers can follow leaders and view a following feed.
    
    Posts are ordered by newest first.
    Optional mode parameter influences content_tone metadata for frontend styling.
    """
    # Role enforcement: raise HTTP 403 if not worshiper
    require_worshiper(current_user)
    
    return get_following_feed(
        db=db,
        worshiper_id=current_user.id,
        page=page,
        page_size=page_size,
        mode=mode
    )


@router.get("/daily-reflection", response_model=DailyReflectionResponse)
def daily_reflection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's guided daily reflection post.
    
    Role Enforcement: Available to ALL authenticated users (worshipers and leaders).
    Everyone benefits from daily reflection.
    
    Returns one meaningful post from the last 24 hours to create a calm,
    focused spiritual moment. No algorithm, no tracking - just the latest
    recent post for daily inspiration.
    
    Returns post=null with graceful message if no posts in last 24 hours.
    """
    return get_daily_reflection(db=db, user_id=current_user.id)
