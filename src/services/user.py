from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ERROR_INVALID_USER_DATA
from src.core.permissions import require_owner_role
from src.core.logger import get_logger
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserCreateByOwner

logger = get_logger(__name__)


class UserService:
    
    @staticmethod
    async def create_user_by_owner(
        db: AsyncSession,
        user_data: UserCreateByOwner
    ) -> User:
        """
        Create a new user account in the system (OWNER role required).
        
        This method allows users with OWNER role to create new user accounts
        with specified roles and credentials. The method validates email uniqueness
        and returns generic error messages to prevent email enumeration attacks.
        
        Args:
            db: Async database session for executing queries
            user_data: UserCreateByOwner schema containing:
                - email (str): User's email address (must be unique)
                - password (str): Plain text password (will be hashed)
                - role (UserRole): User role (OWNER or MEMBER)
        
        Returns:
            User: The newly created user object with hashed password
        
        Raises:
            HTTPException 400: If email already exists (generic error to prevent enumeration)
        
        Security:
            - Password is automatically hashed before storage
            - Generic error messages prevent email enumeration attacks
            - All created users are set to active (is_active = True) by default
            - Only OWNER role can call this endpoint (enforced in API layer)
        
        Note:
            - Email validation is case-sensitive
            - Password complexity requirements should be enforced at schema level
            - Created users can immediately log in with provided credentials
        """
        # Check if email already exists
        existing_user = await UserRepository.get_by_email(db, email=user_data.email)
        if existing_user:
            logger.warning(f"Attempt to create user with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_INVALID_USER_DATA
            )
        
        # Create user using repository
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            is_active=True
        )
        
        logger.info(f"Creating new user with email: {user_data.email}, role: {user_data.role}")
        try:
            new_user = await UserRepository.create(db, user_create)
            logger.info(f"User {new_user.id} created successfully: {new_user.email}")
            return new_user
        except Exception as e:
            logger.error(f"Error creating user {user_data.email}: {str(e)}", exc_info=True)
            raise    
    
    @staticmethod
    async def get_users(
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get list of users.
        
        - OWNER role: Returns all users with pagination
        - MEMBER role: Returns only the current user
        
        Args:
            db: Database session
            current_user: Current authenticated user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
        
        Returns:
            List of User objects
        """
        # Validate OWNER role to get all users
        try:
            require_owner_role(current_user)
            # If OWNER, return all users
            logger.debug(f"User {current_user.id} (OWNER) fetching all users (skip={skip}, limit={limit})")
            users = await UserRepository.get_all(db=db, skip=skip, limit=limit)
            logger.debug(f"Retrieved {len(users)} users for user {current_user.id}")
            return users
        except HTTPException:
            # If not OWNER (member), return only current user
            logger.debug(f"User {current_user.id} (MEMBER) fetching own profile")
            return [current_user]