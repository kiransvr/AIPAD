"""
Database core configuration
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, select
from src.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)

# Parse database URL and extract SSL parameters for asyncpg
db_url = settings.DATABASE_URL
connect_args = {}

# For asyncpg with Neon, we need to configure SSL properly
if "postgresql+asyncpg://" in db_url and "neon.tech" in db_url:
    # Create SSL context for Neon (which requires SSL)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    # Remove URL parameters that asyncpg doesn't recognize
    if "?" in db_url:
        db_url = db_url.split("?")[0]
    
    connect_args = {
        "ssl": ssl_context,
        "timeout": 30,
    }

# Create async engine
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.warning("Database unavailable - API will run without persistence")


async def close_db():
    """Close database connection"""
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
