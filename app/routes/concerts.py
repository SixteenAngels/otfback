from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.concert import Concert
from app.schemas.concert import ConcertCreate, ConcertResponse
from app.routes.auth import get_admin_user

router = APIRouter(prefix="/api/concerts", tags=["concerts"])


@router.post("/", response_model=ConcertResponse)
async def create_concert(
    concert: ConcertCreate,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new concert (admin only)."""
    db_concert = Concert(**concert.dict())
    db.add(db_concert)
    await db.commit()
    await db.refresh(db_concert)
    return db_concert


@router.put("/{concert_id}", response_model=ConcertResponse)
async def update_concert(
    concert_id: int,
    concert_data: ConcertCreate,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update concert details (admin only)."""
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")
    
    # Update fields
    concert.name = concert_data.name
    concert.venue = concert_data.venue
    concert.date = concert_data.date
    concert.description = concert_data.description
    
    await db.commit()
    await db.refresh(concert)
    return concert


@router.get("/{concert_id}", response_model=ConcertResponse)
async def get_concert(concert_id: int, db: AsyncSession = Depends(get_db)):
    """Get concert by ID."""
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")
    return concert


@router.get("/")
async def list_concerts(db: AsyncSession = Depends(get_db)):
    """List all concerts."""
    result = await db.execute(select(Concert))
    return result.scalars().all()


@router.delete("/{concert_id}")
async def delete_concert(
    concert_id: int,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a concert and all associated tickets (admin only)."""
    result = await db.execute(select(Concert).filter(Concert.id == concert_id))
    concert = result.scalars().first()
    if not concert:
        raise HTTPException(status_code=404, detail="Concert not found")
    
    # Delete cascade will remove tickets automatically via foreign key
    await db.delete(concert)
    await db.commit()
    
    return {"message": f"Concert '{concert.name}' deleted successfully", "concert_id": concert_id}
