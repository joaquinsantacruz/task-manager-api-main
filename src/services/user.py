from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ERROR_INVALID_USER_DATA
from src.core.permissions import require_owner_role
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserCreateByOwner


class UserService:
    
    @staticmethod
    async def create_user_by_owner(
        db: AsyncSession,
        user_data: UserCreateByOwner
    ) -> User:
        """
        Create a new user. Validates that the email doesn't exist.
        
        Note: Returns a generic error message to prevent email enumeration attacks.
        """
        # Check if email already exists
        existing_user = await UserRepository.get_by_email(db, email=user_data.email)
        if existing_user:
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
        
        new_user = await UserRepository.create(db, user_create)
        return new_user    
    
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
            return await UserRepository.get_all(db=db, skip=skip, limit=limit)
        except HTTPException:
            # If not OWNER (member), return only current user
            return [current_user]