from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional

from ..dependencies import get_db
from ..models.movie import Movie
from ..models.character import Character
from ..models.associations import movie_character
from ..schemas.movie import MovieResponse, MovieListResponse, CharacterInMovie


router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)


@router.get("", response_model=MovieListResponse)
async def get_movies(
    limit: int = Query(default=10, ge=1, le=100, description="Number of movies to return"),
    offset: int = Query(default=0, ge=0, description="Number of movies to skip"),
    title: Optional[str] = Query(default=None, description="Filter by title (partial match)"),
    original_title_romanised: Optional[str] = Query(default=None, description="Filter by original title romanised (partial match)"),
    director: Optional[str] = Query(default=None, description="Filter by director (partial match)"),
    producer: Optional[str] = Query(default=None, description="Filter by producer (partial match)"),
    release_date: Optional[int] = Query(default=None, description="Filter by release date (exact match)"),
    rt_score: Optional[float] = Query(default=None, description="Filter by minimum RT score"),
    sort: Optional[str] = Query(default="title", description="Field to sort by (title, release_date, rt_score)"),
    order: Optional[str] = Query(default="asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of movies with filtering and sorting.
    
    - **limit**: Number of movies to return (1-100, default: 10)
    - **offset**: Number of movies to skip (default: 0)
    - **title**: Filter by title (case-insensitive partial match)
    - **director**: Filter by director (case-insensitive partial match)
    - **release_date**: Filter by exact release date year
    - **rt_score**: Filter by minimum Rotten Tomatoes score
    - **sort**: Field to sort by (title, release_date, rt_score)
    - **order**: Sort order (asc or desc)
    """
    # Build base query
    query = db.query(Movie)
    
    # Apply filters
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    
    if original_title_romanised:
        query = query.filter(Movie.original_title_romanised.ilike(f"%{original_title_romanised}%"))

    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    
    if producer:
        query = query.filter(Movie.producer.ilike(f"%{producer}%"))
    
    if release_date is not None:
        query = query.filter(Movie.release_date == release_date)
    
    if rt_score is not None:
        query = query.filter(Movie.rt_score >= rt_score)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    sort_field = Movie.title  # default
    if sort == "release_date":
        sort_field = Movie.release_date
    elif sort == "rt_score":
        sort_field = Movie.rt_score
    elif sort == "title":
        sort_field = Movie.title
    
    if order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Apply pagination
    movies = query.offset(offset).limit(limit).all()
    
    return MovieListResponse(
        total=total,
        limit=limit,
        offset=offset,
        movies=movies
    )


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_detail(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific movie, including its characters.
    
    - **movie_id**: The ID of the movie to retrieve
    
    Returns:
    - Movie details with a list of all characters appearing in the movie
    
    Raises:
    - 404: If the movie with the specified ID does not exist
    """
    # Get movie with characters
    movie = db.get(Movie, movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Get characters for this movie
    characters = db.query(Character).join(
        movie_character,
        Character.id == movie_character.c.character_id
    ).filter(
        movie_character.c.movie_id == movie_id
    ).all()
    
    # Convert movie to dict and add characters
    movie_data = MovieResponse.model_validate(movie)
    movie_data.characters = [CharacterInMovie.model_validate(char) for char in characters]
    
    return movie_data


@router.get("/{movie_id}/characters", response_model=list[CharacterInMovie])
async def get_movie_characters(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all characters that appear in a specific movie.
    
    - **movie_id**: The ID of the movie
    
    Returns:
    - List of characters in the movie
    
    Raises:
    - 404: If the movie with the specified ID does not exist
    """
    # Check if movie exists
    movie = db.get(Movie, movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id {movie_id} not found"
        )
    
    # Get characters for this movie
    characters = db.query(Character).join(
        movie_character,
        Character.id == movie_character.c.character_id
    ).filter(
        movie_character.c.movie_id == movie_id
    ).all()
    
    return characters
