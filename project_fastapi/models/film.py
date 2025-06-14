from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from models.genre import Genre
from models.person import Person

class Film(BaseModel):
    uuid: UUID
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genres: Optional[List[Genre]] = []
    actors: Optional[List[Person]] = []
    writers: Optional[List[Person]] = []
    directors: Optional[List[Person]] = []
