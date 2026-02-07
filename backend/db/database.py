"""
Database connection and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager

from .models import Base


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str = None):
        """
        Initialize database connection.

        Args:
            database_url: Database connection string (PostgreSQL)
        """

        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://sapiens:password@localhost:5432/sapiens"
        )

        # Create engine
        # For production, use connection pooling
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables."""

        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables (use with caution!)."""

        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session with automatic cleanup.

        Usage:
            with db.get_session() as session:
                session.query(...)
        """

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """
        Get database session (manual management).

        Usage:
            session = db.get_session_direct()
            try:
                session.query(...)
                session.commit()
            finally:
                session.close()
        """

        return self.SessionLocal()


# Global database instance
db = None


def init_database(database_url: str = None):
    """Initialize global database instance."""

    global db
    db = Database(database_url)
    return db


def get_db() -> Database:
    """Get global database instance."""

    global db
    if db is None:
        db = init_database()
    return db
