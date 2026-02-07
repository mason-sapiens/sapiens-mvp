#!/usr/bin/env python3
"""
Initialize database tables.

Usage:
    python backend/db/init_db.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.db.database import init_database
from backend.db.models import Base


def main():
    """Initialize database."""

    print("Initializing database...")

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL not set")
        print("\nPlease set it with:")
        print("  export DATABASE_URL=postgresql://user:pass@host:port/dbname")
        print("\nOr add it to .env file")
        sys.exit(1)

    print(f"Database URL: {database_url.split('@')[0]}@***")  # Hide credentials

    # Initialize database
    db = init_database(database_url)

    # Create tables
    print("Creating tables...")
    db.create_tables()

    print("✅ Database initialized successfully!")
    print("\nTables created:")
    print("  - user_states")
    print("  - projects")
    print("  - problem_definitions")
    print("  - solution_designs")
    print("  - milestones")
    print("  - conversation_logs")
    print("  - artifact_reviews")
    print("  - state_transitions")


if __name__ == "__main__":
    main()
