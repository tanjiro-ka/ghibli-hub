from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MovieInCharacter(BaseModel):
    """Schema for movie data within a character response."""
    id: int
    ghibli_api_id: str
    title: str
    original_title_romanised: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    release_date: Optional[int] = None
    rt_score: Optional[float] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class CharacterResponse(BaseModel):
    """Schema for character detail response."""
    id: int
    ghibli_api_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Movies list (only for detail endpoint)
    movies: Optional[List[MovieInCharacter]] = None
    
    class Config:
        from_attributes = True


class CharacterListResponse(BaseModel):
    """Schema for paginated character list response."""
    total: int
    limit: int
    offset: int
    characters: List[CharacterResponse]
