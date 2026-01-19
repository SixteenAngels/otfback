from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class TransferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(Enum(TransferStatus), default=TransferStatus.PENDING)
    notes = Column(Text, nullable=True)
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ticket = relationship("Ticket")
    from_user = relationship("User", foreign_keys=[from_user_id], viewonly=True)
    to_user = relationship("User", foreign_keys=[to_user_id], viewonly=True)
