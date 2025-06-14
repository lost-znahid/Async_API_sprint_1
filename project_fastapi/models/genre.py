from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class Genre(BaseModel):
    uuid: UUID
    name: str
    description: Optional[str] = None
