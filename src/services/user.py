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
        Crea un nuevo usuario. Valida que el email no exista.
        """
        # Verificar si el email ya existe
        existing_user = await UserRepository.get_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear el usuario usando el repositorio
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            is_active=True
        )
        
        new_user = await UserRepository.create(db, user_create)
        return new_user
