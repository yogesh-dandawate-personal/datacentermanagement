from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, NullPool, QueuePool
import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)

if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
    logger.warning("Using SQLite database for development/testing")
    # Use SQLite for development/testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    logger.info(f"Using PostgreSQL database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    # Use PostgreSQL with connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_pool_max_overflow,
        pool_pre_ping=settings.database_pool_pre_ping,
        connect_args={
            "connect_timeout": 10,
            "application_name": "netzero-api"
        },
        echo=False,  # Set to True for SQL debugging
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
