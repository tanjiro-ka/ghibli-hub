from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CharacterInMovie(BaseModel):
    """Schema for character data within a movie response."""
    id: int
    ghibli_api_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[str] = None

    class Config:
        from_attributes = True


class MovieResponse(BaseModel):
    """Schema for movie detail response."""
    id: int
    ghibli_api_id: str
    title: str
    original_title: Optional[str] = None
    original_title_romanised: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    release_date: Optional[int] = None
    rt_score: Optional[float] = None
    image_url: Optional[str] = None
    movie_banner: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Characters list (only for detail endpoint)
    characters: Optional[List[CharacterInMovie]] = None

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    """Schema for paginated movie list response."""
    total: int
    limit: int
    offset: int
    movies: List[MovieResponse]
