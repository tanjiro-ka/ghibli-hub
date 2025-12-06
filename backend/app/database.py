from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# database configuration (Docker)
DB_USER = os.getenv("POSTGRES_USER", "ghibli_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ghibli_password")
DB_NAME = os.getenv("POSTGRES_DB", "ghibli_db")
DB_HOST = os.getenv("DB_HOST", "db")  # Docker service name
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True) # echo=True for debugging

# sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for models
Base = declarative_base()

# dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
