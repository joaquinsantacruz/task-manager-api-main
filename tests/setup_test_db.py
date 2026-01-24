"""
Setup script for test database.

This script creates the test database and applies migrations.
Run this before running tests for the first time.

Usage:
    uv run python tests/setup_test_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.db.base import Base
from tests.test_config import test_settings


async def create_test_database():
    """
    Create the test database if it doesn't exist.
    """
    # Extract database name from URL
    db_url = str(test_settings.TEST_DATABASE_URL)
    db_name = db_url.split("/")[-1].split("?")[0]
    
    # Connect to postgres database to create test database
    postgres_url = db_url.replace(f"/{db_name}", "/postgres")
    
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.scalar()
            
            if not exists:
                print(f"Creating database: {db_name}")
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✓ Database '{db_name}' created successfully")
            else:
                print(f"✓ Database '{db_name}' already exists")
    
    finally:
        await engine.dispose()


async def create_tables():
    """
    Create all tables in the test database.
    """
    print("\nCreating database tables...")
    
    # Import models to register them with Base
    from src.models.user import User  # noqa: F401
    from src.models.task import Task  # noqa: F401
    from src.models.comment import Comment  # noqa: F401
    from src.models.notification import Notification  # noqa: F401
    
    engine = create_async_engine(str(test_settings.TEST_DATABASE_URL))
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tables created successfully")
        
        # List created tables
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """)
            )
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\nCreated tables ({len(tables)}):")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("\n⚠ No tables were created")
    
    finally:
        await engine.dispose()


async def verify_setup():
    """
    Verify that the test database is set up correctly.
    """
    print("\n" + "="*50)
    print("Test Database Setup Complete")
    print("="*50)
    print(f"\nDatabase URL: {test_settings.TEST_DATABASE_URL}")
    print("\nYou can now run tests with:")
    print("  pytest")
    print("  pytest -v")
    print("  pytest tests/test_tasks.py")
    print("\n" + "="*50)


async def main():
    """
    Main setup function.
    """
    print("="*50)
    print("Task Manager API - Test Database Setup")
    print("="*50)
    print()
    
    try:
        await create_test_database()
        await create_tables()
        await verify_setup()
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running (docker-compose up -d db)")
        print("  2. Connection details in tests/test_config.py are correct")
        print("  3. User has permission to create databases")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
