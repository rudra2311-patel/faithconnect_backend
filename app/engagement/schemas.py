"""
Schemas for engagement operations.

Simple response models for like/save actions.
"""

from pydantic import BaseModel


class EngagementResponse(BaseModel):
    """
    Generic success response for engagement actions.
    
    UX: Clean feedback for user actions.
    Examples:
    - "Post liked"
    - "Post unliked"
    - "Post saved"
    - "Post unsaved"
    """
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Post liked"
            }
        }
