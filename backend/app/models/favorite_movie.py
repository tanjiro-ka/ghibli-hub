from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class FavoriteMovie(Base):
    """User's favorite movies for quick access and organization."""
    __tablename__ = "favorite_movies"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='uix_user_movie_favorite'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())