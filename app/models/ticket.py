from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class TicketStatus(str, enum.Enum):
    CREATED = "created"              # Initial state
    SOLD_CONFIRMED = "sold_confirmed"  # Seller scanned (Stage 1)
    VERIFIED = "verified"             # Venue scanned and valid (Stage 2)
    DUPLICATE = "duplicate"           # Attempted duplicate scan detected


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    concert_id = Column(Integer, ForeignKey("concerts.id"), index=True)
    ticket_number = Column(String, unique=True, index=True)
    qr_code_data = Column(String)  # Encoded QR data (unique identifier)
    status = Column(Enum(TicketStatus), default=TicketStatus.CREATED)
    buyer_name = Column(String, nullable=True)
    buyer_email = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    
    # Stage 1: Seller confirms sale
    sold_at = Column(DateTime, nullable=True)              # When seller scanned it
    sold_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Seller
    
    # Stage 2: Venue verifies attendance
    verified_at = Column(DateTime, nullable=True)          # When venue scanned it
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Venue scanner
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    concert = relationship("Concert", back_populates="tickets")
    scans = relationship("Scan", back_populates="ticket", cascade="all, delete-orphan")
    sold_by_user = relationship("User", foreign_keys=[sold_by_user_id], viewonly=True)
    verified_by_user = relationship("User", foreign_keys=[verified_by_user_id], viewonly=True)
