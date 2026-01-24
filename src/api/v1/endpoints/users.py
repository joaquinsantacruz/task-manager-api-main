from typing import List, Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User, UserRole
from src.schemas.user import UserResponse, UserCreateByOwner
from src.repositories.user import UserRepository
from src.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> User:
    """
    Obtener información del usuario actual.
    """
    return current_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """
    Obtener lista de usuarios (solo para OWNER).
    """
    # Solo los OWNER pueden ver la lista de usuarios
    if current_user.role != UserRole.OWNER:
        # Si no es owner, solo retornar el usuario actual
        return [current_user]
    
    return await UserRepository.get_all(db=db, skip=skip, limit=limit)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateByOwner,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_owner: Annotated[User, Depends(deps.get_current_owner)],
) -> User:
    """
    Crear un nuevo usuario (solo para OWNER).
    
    Permite a un usuario con rol de OWNER crear nuevos usuarios.
    Se debe proporcionar:
    - email: Email del nuevo usuario
    - password: Contraseña del nuevo usuario
    - role: Rol del nuevo usuario (owner o member)
    """
    return await UserService.create_user_by_owner(db=db, user_data=user_data)

