from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.schemas.user import UserCreate
from src.core.security import get_password_hash

class UserRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[User]:
        """Busca un usuario por su ID."""
        result = await db.scalars(
            select(User).where(User.id == id)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Busca un usuario por su email."""
        result = await db.scalars(
            select(User).where(User.email == email)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene todos los usuarios activos."""
        result = await db.scalars(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return list(result.all())

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """Crea un usuario nuevo hasheando su contraseña."""
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