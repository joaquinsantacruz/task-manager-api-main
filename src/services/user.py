from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreate, UserCreateByOwner
from src.repositories.user import UserRepository


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
                detail="Invalid user data"
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
