from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    """User account with GitHub OAuth authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=True)  # OAuth
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
