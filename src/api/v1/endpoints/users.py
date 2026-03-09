from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from src.api import deps
from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.permissions import require_owner_role
from src.models.user import User
from src.schemas.user import UserResponse, UserCreateByOwner
from src.services.user import UserService


router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> User:
    """
    Get current user information.
    """
    return current_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    user_service: Annotated[UserService, Depends(deps.get_user_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[User]:
    """
    Get list of users (OWNER role only).
    """
    return await user_service.get_users(
        current_user=current_user, 
        skip=skip, 
        limit=limit
    )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreateByOwner,
    user_service: Annotated[UserService, Depends(deps.get_user_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> User:
    """
    Create a new user (OWNER role only).
    
    Allows a user with OWNER role to create new users.
    Required fields:
    - email: Email of the new user
    - password: Password of the new user
    - role: Role of the new user (owner or member)
    """
    require_owner_role(current_user)
    
    return await user_service.create_user_by_owner(user_data=user_in)

