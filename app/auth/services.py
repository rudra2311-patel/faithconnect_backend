from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.auth.models import User
from app.auth.schemas import UserSignup
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserSignup) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_data: User signup data
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If email already exists
    """
    # Normalize email to lowercase
    normalized_email = user_data.email.lower()
    
    # Check if user already exists
    existing_user = get_user_by_email(db, normalized_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user instance
    db_user = User(
        email=normalized_email,
        password_hash=hashed_password,
        name=user_data.name,
        role=user_data.role,
        faith=user_data.faith,
        bio=user_data.bio,
        profile_photo=user_data.profile_photo,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    # Normalize email to lowercase for lookup
    normalized_email = email.lower()
    user = get_user_by_email(db, normalized_email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user
