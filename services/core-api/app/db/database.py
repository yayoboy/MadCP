"""
MadCP - Database Connection and Session Management

This module handles:
- SQLAlchemy engine and session creation
- Database connection lifecycle
- Connection health checks
- Transaction management

Author: MadCP Team
License: MIT
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ============================================================================
# SQLAlchemy Base
# ============================================================================

Base = declarative_base()

# ============================================================================
# Database Engine and Session
# ============================================================================

# Create async engine
engine = None
async_session_maker = None


async def init_db() -> None:
    """
    Initialize database connection pool and session maker.

    This should be called during application startup.
    """
    global engine, async_session_maker

    logger.info("Initializing database connection...")

    # Convert postgresql:// to postgresql+asyncpg:// for async support
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,  # Verify connections before using them
        poolclass=QueuePool if settings.is_production else QueuePool,
    )

    # Create session maker
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("✅ Database connection initialized")

    # Create tables (for development)
    if settings.is_development:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")


async def close_db() -> None:
    """
    Close database connections.

    This should be called during application shutdown.
    """
    global engine

    if engine:
        logger.info("Closing database connections...")
        await engine.dispose()
        logger.info("✅ Database connections closed")


# ============================================================================
# Session Dependency
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session

    Yields:
        AsyncSession: Database session
    """
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


# ============================================================================
# Health Check
# ============================================================================

async def check_database_health() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    if not engine:
        return False

    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


# ============================================================================
# Transaction Context Manager
# ============================================================================

class DatabaseTransaction:
    """
    Context manager for database transactions.

    Usage:
        async with DatabaseTransaction() as session:
            # Perform database operations
            # Transaction will be committed automatically
            # Or rolled back on exception
    """

    def __init__(self):
        self.session: AsyncSession = None

    async def __aenter__(self) -> AsyncSession:
        """Start transaction"""
        if not async_session_maker:
            raise RuntimeError("Database not initialized")

        self.session = async_session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction"""
        if exc_type is not None:
            # Exception occurred, rollback
            await self.session.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            # No exception, commit
            await self.session.commit()

        await self.session.close()


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "Base",
    "engine",
    "async_session_maker",
    "init_db",
    "close_db",
    "get_db",
    "check_database_health",
    "DatabaseTransaction",
]
