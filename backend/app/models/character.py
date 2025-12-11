from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Character(Base):
    """Studio Ghibli character metadata from Ghibli API."""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)

    ghibli_api_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    gender = Column(String, nullable=True, index=True)
    age = Column(Integer, nullable=True, index=True)
    eye_color = Column(String, nullable=True)
    hair_color = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

