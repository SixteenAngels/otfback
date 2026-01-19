from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class ScanType(str, enum.Enum):
    SALE_CONFIRMATION = "sale_confirmation"  # Stage 1: Seller confirms sale
    ATTENDANCE_VERIFY = "attendance_verify"  # Stage 2: Venue verifies attendance


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), index=True)
    scan_type = Column(Enum(ScanType))
    scanned_at = Column(DateTime, default=datetime.utcnow)
    scanned_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who performed scan
    location = Column(String, nullable=True)  # Where the scan happened
    notes = Column(String, nullable=True)

    ticket = relationship("Ticket", back_populates="scans")
    scanned_by_user = relationship("User", back_populates="scans")
