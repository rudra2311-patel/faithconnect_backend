"""
Routes for media file uploads (images and videos).

Handles file uploads to Cloudinary cloud storage for production,
with fallback to local storage for development.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from typing import Optional
import os
import uuid
import shutil
from pathlib import Path
import cloudinary
import cloudinary.uploader
import cloudinary.api

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.config import settings

# Configure Cloudinary
if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    USE_CLOUDINARY = True
else:
    USE_CLOUDINARY = False

router = APIRouter(prefix="/media", tags=["Media"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Subdirectories for organization
IMAGES_DIR = UPLOAD_DIR / "images"
VIDEOS_DIR = UPLOAD_DIR / "videos"
IMAGES_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}

# Max file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return Path(filename).suffix.lower()


def validate_image(file: UploadFile) -> None:
    """Validate image file."""
    ext = get_file_extension(file.filename or "")
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )


def validate_video(file: UploadFile) -> None:
    """Validate video file."""
    ext = get_file_extension(file.filename or "")
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video format. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image file.
    
    Auth Required: Yes (any authenticated user)
    
    Validates:
    - File format (jpg, jpeg, png, webp, gif)
    - File size (max 10 MB)
    
    Returns:
    - URL to access the uploaded image
    
    Example response:
    {
        "url": "http://localhost:8000/uploads/images/abc123.jpg",
        "filename": "abc123.jpg",
        "media_type": "image"
    }
    """
    # Validate file format
    validate_image(file)
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024):.0f} MB"
        )
    
    # Upload to Cloudinary if configured, otherwise use local storage
    if USE_CLOUDINARY:
        try:
            # Generate unique public_id
            unique_id = str(uuid.uuid4())
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                public_id=unique_id,
                folder="faithconnect/images",
                resource_type="image"
            )
            
            return {
                "url": result['secure_url'],
                "filename": unique_id,
                "media_type": "image"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to Cloudinary: {str(e)}"
            )
    else:
        # Local storage fallback (development)
        ext = get_file_extension(file.filename or "")
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = IMAGES_DIR / unique_filename
        
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        return {
            "url": f"{settings.BASE_URL}/uploads/images/{unique_filename}",
            "filename": unique_filename,
            "media_type": "image"
        }


@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a video file.
    
    Auth Required: Yes (any authenticated user)
    
    Validates:
    - File format (mp4, mov, avi, webm)
    - File size (max 50 MB)
    
    Returns:
    - URL to access the uploaded video
    
    Example response:
    {
        "url": "http://localhost:8000/uploads/videos/xyz789.mp4",
        "filename": "xyz789.mp4",
        "media_type": "video"
    }
    """
    # Validate file format
    validate_video(file)
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video too large. Maximum size: {MAX_VIDEO_SIZE / (1024*1024):.0f} MB"
        )
    
    # Upload to Cloudinary if configured, otherwise use local storage
    if USE_CLOUDINARY:
        try:
            # Generate unique public_id
            unique_id = str(uuid.uuid4())
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                public_id=unique_id,
                folder="faithconnect/videos",
                resource_type="video"
            )
            
            return {
                "url": result['secure_url'],
                "filename": unique_id,
                "media_type": "video"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to Cloudinary: {str(e)}"
            )
    else:
        # Local storage fallback (development)
        ext = get_file_extension(file.filename or "")
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = VIDEOS_DIR / unique_filename
        
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        return {
            "url": f"{settings.BASE_URL}/uploads/videos/{unique_filename}",
            "filename": unique_filename,
            "media_type": "video"
        }
