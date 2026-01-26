from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.schemas.user import UserCreate
from src.core.security import get_password_hash
from src.core.constants import DEFAULT_PAGE_SIZE

class UserRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[User]:
        """
        Retrieve a user by their unique identifier.
        
        This method fetches a single user from the database using their ID,
        regardless of their active status.
        
        Args:
            db: Async database session for executing queries
            id: Unique identifier of the user to retrieve
        
        Returns:
            Optional[User]: User object if found, None if no user exists with the given ID
        
        Note:
            - Returns users regardless of is_active status
            - Does not load related entities (tasks, comments, notifications)
            - Returns None rather than raising exception if not found
        """
        result = await db.scalars(
            select(User).where(User.id == id)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        This method is primarily used for authentication and user existence checks.
        Email lookup is case-sensitive and returns users regardless of active status.
        
        Args:
            db: Async database session for executing queries
            email: Email address of the user to find (case-sensitive)
        
        Returns:
            Optional[User]: User object if found, None if no user exists with the given email
        
        Note:
            - Email matching is case-sensitive
            - Returns users regardless of is_active status
            - Used by authentication system to validate credentials
            - Used to prevent duplicate email registrations
        """
        result = await db.scalars(
            select(User).where(User.email == email)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> List[User]:
        """
        Retrieve all active users in the system with pagination.
        
        This method returns only active users (is_active = True), filtering out
        any deactivated or suspended accounts.
        
        Args:
            db: Async database session for executing queries
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of users to return (default: DEFAULT_PAGE_SIZE)
        
        Returns:
            List[User]: List of active user objects. Returns empty list if no active users exist.
        
        Note:
            - Only returns users where is_active = True
            - Includes both OWNER and MEMBER roles
            - Does not load related entities (tasks, comments)
            - Suitable for user management interfaces
        """
        result = await db.scalars(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return list(result.all())

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Create a new user account with securely hashed password.
        
        This method creates a new user in the database, automatically hashing
        the provided password for secure storage. The user is committed to the
        database immediately.
        
        Args:
            db: Async database session for executing queries
            user_in: UserCreate schema containing:
                - email: User's email address (must be unique)
                - password: Plain text password (will be hashed)
                - role: User role (OWNER or MEMBER)
                - is_active: Account activation status
        
        Returns:
            User: Newly created user object with:
                - Auto-generated ID
                - hashed_password (original password is not stored)
                - All fields from user_in
                - Timestamps (created_at, updated_at) auto-populated
        
        Note:
            - Password is automatically hashed using bcrypt
            - Plain text password is never stored in database
            - Email uniqueness must be validated before calling
            - Commits transaction immediately
        """
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=user_in.is_active
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user