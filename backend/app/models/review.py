from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='uix_user_movie_review'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())