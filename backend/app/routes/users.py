from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..models.review import Review
from ..models.favorite_movie import FavoriteMovie
from ..models.favorite_character import FavoriteCharacter
from ..schemas.user import UserResponse, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile with statistics.
    
    Requires authentication.
    """
    # Calculate statistics
    reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == current_user.id).scalar()
    favorites_movies_count = db.query(func.count(FavoriteMovie.id)).filter(FavoriteMovie.user_id == current_user.id).scalar()
    favorites_characters_count = db.query(func.count(FavoriteCharacter.id)).filter(FavoriteCharacter.user_id == current_user.id).scalar()
    
    # Build response with statistics
    user_data = UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        github_id=current_user.github_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        reviews_count=reviews_count or 0,
        favorites_movies_count=favorites_movies_count or 0,
        favorites_characters_count=favorites_characters_count or 0
    )
    
    return user_data


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user public profile with statistics.
    
    Returns user information including:
    - Basic profile (id, email, display_name, avatar_url)
    - Statistics (reviews_count, favorites_movies_count, favorites_characters_count)
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Calculate statistics
    reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == user_id).scalar()
    favorites_movies_count = db.query(func.count(FavoriteMovie.id)).filter(FavoriteMovie.user_id == user_id).scalar()
    favorites_characters_count = db.query(func.count(FavoriteCharacter.id)).filter(FavoriteCharacter.user_id == user_id).scalar()
    
    # Build response with statistics
    user_data = UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        github_id=user.github_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        reviews_count=reviews_count or 0,
        favorites_movies_count=favorites_movies_count or 0,
        favorites_characters_count=favorites_characters_count or 0
    )
    
    return user_data


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current authenticated user profile.
    
    Allowed fields to update:
    - display_name (optional)
    - avatar_url (optional)
    
    Email and GitHub ID cannot be changed.
    Requires authentication.
    """
    # Update only provided fields
    if user_update.display_name is not None:
        current_user.display_name = user_update.display_name
    
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    # Commit changes
    db.commit()
    db.refresh(current_user)
    
    # Calculate statistics for response
    reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == current_user.id).scalar()
    favorites_movies_count = db.query(func.count(FavoriteMovie.id)).filter(FavoriteMovie.user_id == current_user.id).scalar()
    favorites_characters_count = db.query(func.count(FavoriteCharacter.id)).filter(FavoriteCharacter.user_id == current_user.id).scalar()
    
    # Build response
    user_data = UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        github_id=current_user.github_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        reviews_count=reviews_count or 0,
        favorites_movies_count=favorites_movies_count or 0,
        favorites_characters_count=favorites_characters_count or 0
    )
    
    return user_data
