#!/usr/bin/env python3
"""
Database initialization script for StoryQuest.
Run this to create or reset the database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config
from app.db.database import Database
from app.db.models import Base


async def init_database():
    """Initialize the database and create all tables."""
    print("StoryQuest Database Initialization")
    print("=" * 50)

    # Load configuration
    config = get_config()
    print(f"Database URL: {config.database.url}")

    # Create database instance
    db = Database(config.database)

    try:
        # Create tables
        if db.is_async:
            print("Using async database engine...")
            async with db.engine.begin() as conn:
                # Drop all tables (for fresh start)
                await conn.run_sync(Base.metadata.drop_all)
                print("Dropped existing tables (if any)")

                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                print("Created all tables")
        else:
            print("Using sync database engine...")
            # Drop all tables (for fresh start)
            Base.metadata.drop_all(bind=db.engine)
            print("Dropped existing tables (if any)")

            # Create all tables
            Base.metadata.create_all(bind=db.engine)
            print("Created all tables")

        print("\nDatabase tables:")
        for table in Base.metadata.tables.keys():
            print(f"  - {table}")

        print("\n✅ Database initialization complete!")

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise
    finally:
        await db.close()


def main():
    """Main entry point."""
    asyncio.run(init_database())


if __name__ == "__main__":
    main()
