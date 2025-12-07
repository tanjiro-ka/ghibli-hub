from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from ..database import Base

class Movie(Base):
    """Studio Ghibli movie metadata from Ghibli API."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)

    ghibli_api_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    original_title = Column(String, nullable=True)
    original_title_romanised = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    director = Column(String, nullable=True, index=True)
    producer = Column(String, nullable=True, index=True)
    release_date = Column(Integer, nullable=True, index=True)
    rt_score = Column(Float, nullable=True, default=0.0, index=True)
    image_url = Column(String, nullable=True)
    movie_banner = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
