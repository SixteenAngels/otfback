from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database import get_db
from app.models.scan import Scan, ScanType
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse
from app.routes.auth import get_current_user, get_scanner_user

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan: ScanCreate,
    current_user: User = Depends(get_scanner_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a ticket scan (scanner or admin).
    Verification users (verify*) can only scan once per ticket.
    Sales users (sales*) can scan multiple times.
    """
    result = await db.execute(select(Ticket).filter(Ticket.id == scan.ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if current user is a verification user
    is_verify_user = current_user.username.startswith('verify')
    
    # Verification users cannot rescan already-verified tickets
    if is_verify_user and ticket.status == TicketStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already verified - cannot rescan"
        )
    
    # Create scan record
    db_scan = Scan(
        ticket_id=scan.ticket_id,
        scan_type=scan.scan_type,
        scanned_by_user_id=current_user.id,
        location=scan.location,
        notes=scan.notes
    )
    db.add(db_scan)
    
    # Update ticket status based on user type and scan type
    if is_verify_user:
        # Verify users mark ticket as VERIFIED (immutable afterwards)
        ticket.status = TicketStatus.VERIFIED
        ticket.verified_by_user_id = current_user.id
        ticket.verified_at = datetime.utcnow()
    else:
        # Sales users use scan_type to update status
        if scan.scan_type == ScanType.SALE_CONFIRMATION:
            ticket.status = TicketStatus.SOLD_CONFIRMED
        elif scan.scan_type == ScanType.ENTRY_CHECK:
            ticket.status = TicketStatus.VERIFIED
        elif scan.scan_type == ScanType.ATTENDANCE:
            ticket.status = TicketStatus.VERIFIED
    
    ticket.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_scan)
    return db_scan


@router.get("/ticket/{ticket_id}")
async def get_ticket_scans(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """Get all scans for a specific ticket."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    result = await db.execute(select(Scan).filter(Scan.ticket_id == ticket_id))
    scans = result.scalars().all()
    return scans


@router.get("/concert/{concert_id}/attendance")
async def get_concert_attendance(concert_id: int, db: AsyncSession = Depends(get_db)):
    """Get attendance statistics for a concert."""
    # Get all scans for tickets belonging to this concert
    result = await db.execute(
        select(Scan).join(Ticket).filter(
            (Ticket.concert_id == concert_id) &
            (Scan.scan_type == ScanType.ATTENDANCE_VERIFY)
        )
    )
    attendance_scans = result.scalars().all()
    
    attended_tickets = set(scan.ticket_id for scan in attendance_scans)
    
    # Get all sold tickets for this concert
    result = await db.execute(
        select(Ticket).filter(
            (Ticket.concert_id == concert_id) &
            (Ticket.status.in_([TicketStatus.SOLD_CONFIRMED, TicketStatus.VERIFIED]))
        )
    )
    sold_tickets = result.scalars().all()
    
    return {
        "concert_id": concert_id,
        "total_sold": len(sold_tickets),
        "total_attended": len(attended_tickets),
        "attendance_rate": f"{len(attended_tickets) / len(sold_tickets) * 100:.1f}%" if sold_tickets else "0%"
    }
