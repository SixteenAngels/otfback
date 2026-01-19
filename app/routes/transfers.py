from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database import get_db
from app.models.transfer import Transfer, TransferStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferRespond, TransferResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


@router.post("/initiate", response_model=TransferResponse)
async def initiate_transfer(
    transfer_data: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initiate a ticket transfer to another user."""
    # Check if ticket exists
    result = await db.execute(select(Ticket).filter(Ticket.id == transfer_data.ticket_id))
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check if ticket is sold and user owns it
    if ticket.status != TicketStatus.SOLD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only sold tickets can be transferred"
        )
    
    # Check if to_user exists
    result = await db.execute(select(User).filter(User.id == transfer_data.to_user_id))
    to_user = result.scalars().first()
    
    if not to_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    # Create transfer request
    db_transfer = Transfer(
        ticket_id=transfer_data.ticket_id,
        from_user_id=current_user.id,
        to_user_id=transfer_data.to_user_id,
        notes=transfer_data.notes
    )
    
    db.add(db_transfer)
    ticket.status = TicketStatus.TRANSFERRED
    await db.commit()
    await db.refresh(db_transfer)
    
    return db_transfer


@router.get("/pending", response_model=list[TransferResponse])
async def get_pending_transfers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending transfers for current user."""
    result = await db.execute(
        select(Transfer).filter(
            (Transfer.to_user_id == current_user.id) &
            (Transfer.status == TransferStatus.PENDING)
        )
    )
    transfers = result.scalars().all()
    return transfers


@router.post("/{transfer_id}/accept", response_model=TransferResponse)
async def accept_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a transfer request."""
    result = await db.execute(select(Transfer).filter(Transfer.id == transfer_id))
    transfer = result.scalars().first()
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    if transfer.to_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot accept this transfer"
        )
    
    if transfer.status != TransferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer has already been processed"
        )
    
    transfer.status = TransferStatus.ACCEPTED
    transfer.completed_at = datetime.utcnow()
    
    # Update ticket ownership
    result = await db.execute(select(Ticket).filter(Ticket.id == transfer.ticket_id))
    ticket = result.scalars().first()
    ticket.current_holder_id = current_user.id
    ticket.status = TicketStatus.SOLD
    
    await db.commit()
    await db.refresh(transfer)
    
    return transfer


@router.post("/{transfer_id}/reject", response_model=TransferResponse)
async def reject_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a transfer request."""
    result = await db.execute(select(Transfer).filter(Transfer.id == transfer_id))
    transfer = result.scalars().first()
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    if transfer.to_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot reject this transfer"
        )
    
    if transfer.status != TransferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer has already been processed"
        )
    
    transfer.status = TransferStatus.REJECTED
    
    # Revert ticket status
    result = await db.execute(select(Ticket).filter(Ticket.id == transfer.ticket_id))
    ticket = result.scalars().first()
    ticket.status = TicketStatus.SOLD
    
    await db.commit()
    await db.refresh(transfer)
    
    return transfer


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transfer details."""
    result = await db.execute(select(Transfer).filter(Transfer.id == transfer_id))
    transfer = result.scalars().first()
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    return transfer
