from pydantic import BaseModel
from datetime import datetime
from typing import List

class DocumentResponse(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime

    class Config:
        from_attributes = True