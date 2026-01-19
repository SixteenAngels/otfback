from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class TicketStatus(str, Enum):
    CREATED = "created"
    SOLD = "sold"
    SCANNED_ENTRY = "scanned_entry"
    ATTENDED = "attended"


class TicketBase(BaseModel):
    concert_id: int
    buyer_name: Optional[str] = None
    buyer_email: Optional[str] = None
    price: Optional[int] = None  # In cents


class TicketCreate(TicketBase):
    pass


class TicketMarkSold(BaseModel):
    buyer_name: str
    buyer_email: str
    price: int


class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    qr_code_data: str
    status: TicketStatus
    sold_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
