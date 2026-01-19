from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
from typing import List
from io import BytesIO
import zipfile

from app.database import get_db
from app.models.ticket import Ticket, TicketStatus
from app.models.concert import Concert
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketResponse, TicketMarkSold
from app.utils.qr_generator import generate_qr_code
from app.routes.auth import get_current_user, get_admin_user, get_scanner_user
from fastapi.responses import StreamingResponse
import base64

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


class BatchCreateRequest(BaseModel):
    quantity: int


class BatchCreateResponse(BaseModel):
    created_count: int
    concert_id: int
    ticket_numbers: List[str]


@router.post("/create/{concert_id}", response_model=TicketResponse)
async def create_ticket(
    concert_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new ticket for a concert.
    QR code is generated automatically (admin only).
    """
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")

    ticket_number = str(uuid4())[:12].upper()
    
    # Generate QR code (image base64 + payload)
    qr_base64, qr_data = generate_qr_code(0, ticket_number, concert_id)
    
    db_ticket = Ticket(
        concert_id=concert_id,
        ticket_number=ticket_number,
        qr_code_data=qr_base64,
        status=TicketStatus.CREATED
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    
    return db_ticket


@router.post("/batch/create/{concert_id}", response_model=BatchCreateResponse)
async def create_batch_tickets(
    concert_id: int,
    request: BatchCreateRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple tickets for a concert in batch (admin only).
    """
    if request.quantity <= 0 or request.quantity > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be between 1 and 5000"
        )
    
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")

    tickets = []
    ticket_numbers = []
    
    for i in range(request.quantity):
        ticket_number = str(uuid4())[:12].upper()
        qr_base64, qr_data = generate_qr_code(i, ticket_number, concert_id)
        
        db_ticket = Ticket(
            concert_id=concert_id,
            ticket_number=ticket_number,
            qr_code_data=qr_base64,
            status=TicketStatus.CREATED
        )
        tickets.append(db_ticket)
        ticket_numbers.append(ticket_number)
    
    db.add_all(tickets)
    await db.commit()
    
    return BatchCreateResponse(
        created_count=len(tickets),
        concert_id=concert_id,
        ticket_numbers=ticket_numbers
    )


@router.get("/{ticket_id}/qr-code")
async def get_qr_code(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """Get QR code image as base64."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "qr_code": ticket.qr_code_data,
        "status": ticket.status
    }


@router.get("/dev/random-qr")
async def dev_random_qr(size: int = 29, module_size: int = 10, border: int = 4):
    """Development endpoint: return a random QR-like PNG image."""
    from app.utils.random_qr import get_png_bytes
    png = get_png_bytes(size=size, module_size=module_size, border=border)
    return StreamingResponse(BytesIO(png), media_type="image/png")


@router.post("/{ticket_id}/mark-sold", response_model=TicketResponse)
async def mark_ticket_sold(
    ticket_id: int,
    data: TicketMarkSold,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a ticket as sold and add buyer information (admin only)."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = TicketStatus.SOLD
    ticket.buyer_name = data.buyer_name
    ticket.buyer_email = data.buyer_email
    ticket.price = data.price
    ticket.sold_at = datetime.utcnow()
    ticket.original_buyer_id = current_user.id
    ticket.current_holder_id = current_user.id
    
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """Get ticket details by ID."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/concert/{concert_id}")
async def list_concert_tickets(concert_id: int, db: AsyncSession = Depends(get_db)):
    """List all tickets for a concert."""
    result = await db.execute(select(Ticket).filter(Ticket.concert_id == concert_id))
    return result.scalars().all()


@router.get("/number/{ticket_number}", response_model=TicketResponse)
async def get_ticket_by_number(ticket_number: str, db: AsyncSession = Depends(get_db)):
    """Get ticket by ticket number (useful for QR scanner)."""
    result = await db.execute(select(Ticket).filter(Ticket.ticket_number == ticket_number))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/concert/{concert_id}/qr-codes/download")
async def download_all_qr_codes(
    concert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download all QR codes for a concert as ZIP file."""
    # Get concert
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")
    
    # Get all tickets
    result = await db.execute(select(Ticket).filter(Ticket.concert_id == concert_id))
    tickets = result.scalars().all()
    
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this concert")
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for ticket in tickets:
            if ticket.qr_code_data:
                # Decode base64 and add to zip
                qr_image_data = base64.b64decode(ticket.qr_code_data)
                filename = f"QR_{ticket.ticket_number}.png"
                zip_file.writestr(filename, qr_image_data)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=qr-codes-{concert.name}.zip"}
    )


@router.get("/{ticket_id}/download-qr")
async def download_single_qr(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download a single QR code as PNG image."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket.qr_code_data:
        raise HTTPException(status_code=404, detail="No QR code for this ticket")
    
    # Decode base64 to PNG bytes
    qr_image_data = base64.b64decode(ticket.qr_code_data)
    
    return StreamingResponse(
        BytesIO(qr_image_data),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=QR_{ticket.ticket_number}.png"}
    )


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a ticket (admin only)."""
    result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket_number = ticket.ticket_number
    await db.delete(ticket)
    await db.commit()
    
    return {"message": f"Ticket {ticket_number} deleted successfully", "ticket_id": ticket_id}
