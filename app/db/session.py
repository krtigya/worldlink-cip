"""
Here I am writing code for the Async SQLAlchemy session factory.
app/db/session.py — Async SQLAlchemy session factory.
Uses asyncpg driver for high-performance async DB access.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.config import get_settings

settings = get_settings()

# Async engine (used by FastAPI endpoints)
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=not settings.is_production,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine (used by Celery workers + Alembic)
sync_engine = create_engine(
    settings.database_url_sync,
    pool_size=10,
    pool_recycle=1800,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """Celery worker dependency — yields a sync DB session."""
    from sqlalchemy.orm import sessionmaker, Session
    SyncSession = sessionmaker(bind=sync_engine, expire_on_commit=False)
    session: Session = SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
