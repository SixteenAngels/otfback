from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.settings import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    poolclass=NullPool,  # Use NullPool for serverless/neon
)

# Create async session factory
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db():
    """Get async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
