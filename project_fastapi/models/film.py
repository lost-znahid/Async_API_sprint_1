from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from models.genre import Genre
from models.person import Person

class Film(BaseModel):
    uuid: UUID
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genres: Optional[List[Genre]] = Field(default_factory=list)
    actors: Optional[List[Person]] = Field(default_factory=list)
    writers: Optional[List[Person]] = Field(default_factory=list)
    directors: Optional[List[Person]] = Field(default_factory=list)
