from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import Optional

from ..dependencies import get_db
from ..models.character import Character
from ..schemas.character import CharacterResponse, CharacterListResponse, MovieInCharacter


router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)


@router.get("", response_model=CharacterListResponse)
async def get_characters(
    limit: int = Query(default=10, ge=1, le=100, description="Number of characters to return"),
    offset: int = Query(default=0, ge=0, description="Number of characters to skip"),
    name: str = Query(default=None, description="Filter by name (partial match)"),
    gender: Optional[str] = Query(default=None, description="Filter by gender (partial match)"),
    age: Optional[int] = Query(default=None, description="Filter by minimun age"),
    sort: Optional[str] = Query(default="name", description="Field to sort by (name, gender, age)"),
    order: Optional[str] = Query(default="asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of characters with filtering and sorting.
    
    - **limit**: Number of characters to return (1-100, default: 10)
    - **offset**: Number of characters to skip (default: 0)
    - **name**: Filter by name (case-insensitive partial match)
    - **gender**: Filter by gender (case-insensitive partial match)
    - **age**: Filter by minimum age
    - **sort**: Field to sort by (title, release_date, rt_score)
    - **order**: Sort order (asc or desc)
    """
    # Build base query
    query = db.query(Character)
    
    # Apply filters
    if name:
        query = query.filter(Character.name.ilike(f"%{name}%"))
    
    if gender:
        query = query.filter(Character.gender.ilike(f"%{gender}%"))

    if age is not None:
        query = query.filter(Character.age >= age)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    sort_mapping = {"name": Character.name, "gender": Character.gender, "age": Character.age}
    sort_field = sort_mapping.get(sort, Character.name) # Character.name default
    
    order_by = desc if order == "desc" else asc
    query = query.order_by(order_by(sort_field))
    
    # Apply pagination
    characters = query.offset(offset).limit(limit).all()
    
    return CharacterListResponse(
        total=total,
        limit=limit,
        offset=offset,
        characters=characters
    )

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character_detail(
    character_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific character, including its movies.
    
    - **character_id**: The ID of the character to retrieve
    
    Returns:
    - Character details with a list of all movies where character appears
    
    Raises:
    - 404: If the character with the specified ID does not exist
    """
    # Get character with movies
    character = db.get(Character, character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found"
        )
    
    # Get movies for this character
    movies = db.query(Movie).join(
        movie_character,
        Movie.id == movie_character.c.movie_id
    ).filter(
        movie_character.c.character_id == character_id
    ).all()
    
    # Convert character to dict and add movies
    character_data = CharacterResponse.model_validate(character)
    character_data.movies = [MovieInCharacter.model_validate(mov) for mov in movies]
    
    return character_data


@router.get("/{character_id}/movies", response_model=list[MovieInCharacter])
async def get_character_movies(
    character_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all movies where a specific character appears.
    
    - **character_id**: The ID of the character
    
    Returns:
    - List of movies for a character
    
    Raises:
    - 404: If the character with the specified ID does not exist
    """
    # Check if character exists
    character = db.get(Character, character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found"
        )
    
    # Get movies for this character
    movies = db.query(Movie).join(
        movie_character,
        Movie.id == movie_character.c.movie_id
    ).filter(
        movie_character.c.character_id == character_id
    ).all()
    
    return movies