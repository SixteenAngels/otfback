"""Initialize database tables"""
import asyncio
from app.database import engine
from app.models.base import Base

async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialization complete.")
