"""
Test fixtures and configuration.

This module provides pytest fixtures for integration testing.
Fixtures follow the Dependency Inversion Principle by providing
abstractions for database, authentication, and API client setup.

Fixtures are scoped appropriately to balance test isolation and performance:
- session: Created once per test session
- function: Created for each test function (default, ensures isolation)
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.db.base import Base
from src.db.session import get_db
from src.models.user import User, UserRole
from src.core.security import get_password_hash, create_access_token
from tests.test_config import test_settings


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.
    
    This fixture ensures all async tests share the same event loop,
    which is required for session-scoped async fixtures.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """
    Create a test database engine for the entire test session.
    
    Uses NullPool to avoid connection pool issues in testing.
    The engine is created once and reused across all tests for performance.
    """
    engine = create_async_engine(
        str(test_settings.TEST_DATABASE_URL),
        poolclass=NullPool,
        echo=False,  # Set to True for SQL debugging
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_setup(test_engine):
    """
    Set up and tear down the test database schema for each test.
    
    This fixture:
    1. Creates all tables before the test
    2. Yields control to the test
    3. Drops all tables after the test
    
    Using function scope ensures complete isolation between tests,
    following the Interface Segregation Principle - each test gets
    a clean database state.
    """
    # Import all models to ensure they are registered with Base.metadata
    from src.models.task import Task  # noqa: F401
    from src.models.comment import Comment  # noqa: F401
    from src.models.notification import Notification  # noqa: F401
    
    async with test_engine.begin() as conn:
        # First drop all tables to ensure clean state
        await conn.run_sync(Base.metadata.drop_all)
        # Then create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(test_engine, test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for each test function.
    
    This fixture creates a new session for each test, ensuring isolation.
    The session is automatically rolled back after the test to maintain
    a clean state.
    
    Yields:
        AsyncSession: A database session for the test to use
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an HTTP client for testing API endpoints.
    
    This fixture:
    1. Overrides the database dependency with the test database session
    2. Creates an async HTTP client for making requests
    3. Cleans up after the test
    
    Following the Dependency Inversion Principle, this allows tests to
    interact with the API through a stable interface while using a test
    database underneath.
    
    Yields:
        AsyncClient: An HTTP client configured for testing
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True  # Follow 307 redirects automatically
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def test_user_owner(db_session: AsyncSession) -> User:
    """
    Create a test user with OWNER role.
    
    This fixture provides a pre-configured owner user for tests that
    require elevated permissions. Follows the Factory pattern for
    creating test data.
    
    Returns:
        User: A user with OWNER role
    """
    user = User(
        email="owner@test.com",
        hashed_password=get_password_hash("ownerpassword123"),
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_user_member(db_session: AsyncSession) -> User:
    """
    Create a test user with MEMBER role.
    
    This fixture provides a pre-configured member user for tests that
    require standard user permissions.
    
    Returns:
        User: A user with MEMBER role
    """
    user = User(
        email="member@test.com",
        hashed_password=get_password_hash("memberpassword123"),
        role=UserRole.MEMBER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def owner_token(test_user_owner: User) -> str:
    """
    Generate a JWT token for the owner user.
    
    This fixture creates a valid JWT token that can be used in
    Authorization headers for authenticated requests.
    
    Args:
        test_user_owner: The owner user fixture
        
    Returns:
        str: A valid JWT token
    """
    return create_access_token(subject=test_user_owner.email)


@pytest.fixture(scope="function")
def member_token(test_user_member: User) -> str:
    """
    Generate a JWT token for the member user.
    
    This fixture creates a valid JWT token for a member user.
    
    Args:
        test_user_member: The member user fixture
        
    Returns:
        str: A valid JWT token
    """
    return create_access_token(subject=test_user_member.email)


@pytest.fixture(scope="function")
def auth_headers_owner(owner_token: str) -> dict:
    """
    Create authentication headers for owner user.
    
    Provides properly formatted headers for authenticated requests.
    Follows the Single Responsibility Principle - only handles
    header formatting.
    
    Args:
        owner_token: JWT token for owner user
        
    Returns:
        dict: Headers dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {owner_token}"}


@pytest.fixture(scope="function")
def auth_headers_member(member_token: str) -> dict:
    """
    Create authentication headers for member user.
    
    Args:
        member_token: JWT token for member user
        
    Returns:
        dict: Headers dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {member_token}"}
