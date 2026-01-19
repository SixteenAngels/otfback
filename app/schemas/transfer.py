from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class TransferStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TransferCreate(BaseModel):
    ticket_id: int
    to_user_id: int
    notes: Optional[str] = None


class TransferRespond(BaseModel):
    status: TransferStatus  # ACCEPTED or REJECTED
    notes: Optional[str] = None


class TransferResponse(BaseModel):
    id: int
    ticket_id: int
    from_user_id: int
    to_user_id: int
    status: TransferStatus
    notes: Optional[str]
    initiated_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
