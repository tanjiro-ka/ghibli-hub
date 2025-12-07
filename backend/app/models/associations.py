from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

movie_character = Table(
    'movie_character',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)