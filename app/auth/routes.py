from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.schemas import UserSignup, UserLogin, SignupResponse, TokenResponse, UserResponse, UpdateProfile
from app.auth.services import create_user, authenticate_user
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new user and return access token.
    
    - **email**: Valid email address (case-insensitive)
    - **password**: Minimum 8 characters
    - **name**: User's full name
    - **role**: Either "worshiper" or "leader"
    - **faith**: Required for worshipers, optional for leaders
    - **bio**: Optional, typically for leaders
    - **profile_photo**: Optional URL to profile photo
    
    Returns JWT access token and user info for immediate login.
    """
    # Create user
    user = create_user(db, user_data)
    
    # Create access token (auto-login after signup)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Returns JWT access token on successful authentication.
    """
    # Authenticate user
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    profile_data: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current authenticated user's profile.
    
    Only updates fields that are provided in the request.
    Cannot update: email, role, id, password (use separate endpoint for password).
    
    - **faith**: Faith tradition (optional, max 100 chars)
    - **bio**: User biography (optional, max 500 chars, mainly for leaders)
    - **profile_photo**: URL to profile photo (optional)
    
    Returns the updated user profile.
    """
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # Commit changes
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
    
    return current_user
