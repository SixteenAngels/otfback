from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ConcertBase(BaseModel):
    name: str
    date: datetime
    venue: str
    description: Optional[str] = None


class ConcertCreate(ConcertBase):
    pass


class ConcertResponse(ConcertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
