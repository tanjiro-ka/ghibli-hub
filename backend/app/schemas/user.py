from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserUpdate(BaseModel):
    """Schema for updating user profile (only editable fields)."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserResponse(BaseModel):
    """Schema for user public profile response with statistics."""
    id: int
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    github_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Statistics
    reviews_count: int = 0
    favorites_movies_count: int = 0
    favorites_characters_count: int = 0

    class Config:
        from_attributes = True  # Allows Pydantic to work with SQLAlchemy models
