from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class FavoriteCharacter(Base):
    """User's favorite characters for quick access and organization."""
    __tablename__ = "favorite_characters"
    __table_args__ = (UniqueConstraint('user_id', 'character_id', name='uix_user_character_favorite'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())