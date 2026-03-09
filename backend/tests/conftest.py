"""
Pytest configuration and fixtures for iNetZero backend tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a test database session using SQLite in-memory
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create session
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
