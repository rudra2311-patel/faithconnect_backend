from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.auth.models import UserRole


# ==================== Request Schemas ====================

class UserSignup(BaseModel):
    """Schema for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=1, max_length=100)
    role: UserRole
    faith: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_photo: Optional[str] = None

    @field_validator('faith')
    @classmethod
    def validate_faith_for_worshiper(cls, v, info):
        """Ensure worshipers provide a faith."""
        role = info.data.get('role')
        if role == UserRole.WORSHIPER:
            if not v or (isinstance(v, str) and not v.strip()):
                raise ValueError('Faith is required for worshipers')
        # Return stripped value or original
        return v.strip() if (v and isinstance(v, str)) else v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UpdateProfile(BaseModel):
    """Schema for updating user profile.
    
    All fields are optional - only provided fields will be updated.
    Users cannot change email, role, or id through this endpoint.
    """
    faith: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    profile_photo: Optional[str] = None


# ==================== Response Schemas ====================

class SignupResponse(BaseModel):
    """Schema for signup response (no JWT token)."""
    message: str = "User created successfully"
    user_id: int
    role: UserRole


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: UserRole


class UserResponse(BaseModel):
    """Schema for user profile response (no password)."""
    id: int
    email: str
    name: str
    role: UserRole
    faith: Optional[str] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
