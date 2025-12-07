from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base


class MovieStatusEnum(PyEnum):
    """Status values for user movie interactions."""
    watched = "watched"
    want_to_watch = "want_to_watch"


class MovieStatus(Base):
    __tablename__ = "movie_status"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='uix_user_movie_status'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)
    
    status = Column(Enum(MovieStatusEnum), nullable=False)
    watched_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())