from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ScanType(str, Enum):
    SALE_CONFIRMATION = "sale_confirmation"
    ENTRY_CHECK = "entry_check"
    ATTENDANCE = "attendance"


class ScanCreate(BaseModel):
    ticket_id: int
    scan_type: ScanType
    scanner_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class ScanResponse(BaseModel):
    id: int
    ticket_id: int
    scan_type: ScanType
    scanned_at: datetime
    scanner_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
