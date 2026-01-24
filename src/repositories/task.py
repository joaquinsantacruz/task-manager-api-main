from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate

class TaskRepository:
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, id: int
    ) -> Optional[Task]:
        """Busca una tarea solo por su ID (owner use)."""
        query = select(Task).options(selectinload(Task.owner)).where(Task.id == id)
        result = await db.scalars(query)
        return result.one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, obj_in: TaskCreate, owner_id: int
    ) -> Task:
        """Crea una tarea asignada al usuario actual."""
        db_obj = Task(
            **obj_in.model_dump(),
            owner_id=owner_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Cargar la relación owner
        await db.refresh(db_obj, ["owner"])
        return db_obj

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Devuelve todas las tareas (owner use)."""
        query = select(Task).options(selectinload(Task.owner)).offset(skip).limit(limit)
        result = await db.scalars(query)
        return list(result.all())

    @staticmethod
    async def get_multi_by_owner(
        db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Devuelve solo las tareas del usuario logueado."""
        query = select(Task).options(selectinload(Task.owner)).where(Task.owner_id == owner_id).offset(skip).limit(limit)
        result = await db.scalars(query)
        return list(result.all())

    @staticmethod
    async def get_by_id_and_owner(
        db: AsyncSession, id: int, owner_id: int
    ) -> Optional[Task]:
        """Busca una tarea específica, asegurando que pertenezca al usuario."""
        query = select(Task).options(selectinload(Task.owner)).where(Task.id == id, Task.owner_id == owner_id)
        result = await db.scalars(query)
        return result.one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession, db_obj: Task, obj_in: TaskUpdate
    ) -> Task:
        """Actualiza los campos enviados."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Cargar la relación owner
        await db.refresh(db_obj, ["owner"])
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, db_obj: Task) -> None:
        """Elimina la tarea."""
        await db.delete(db_obj)
        await db.commit()