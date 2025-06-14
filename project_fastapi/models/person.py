from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class Person(BaseModel):
    uuid: UUID
    full_name: str
    roles: Optional[List[str]] = []
