from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.models.user import User, UserRole
from src.models.task import Task
from src.repositories.task import TaskRepository
from src.repositories.user import UserRepository
from src.core.permissions import require_owner_role, require_task_modification

class TaskService:
    
    @staticmethod
    async def get_tasks_for_user(
        db: AsyncSession, 
        user: User, 
        skip: int = 0, 
        limit: int = 100,
        only_mine: bool = False
    ) -> List[Task]:
        
        if only_mine or user.role != UserRole.OWNER:
            return await TaskRepository.get_multi_by_owner(
                db=db, owner_id=user.id, skip=skip, limit=limit
            )
        
        return await TaskRepository.get_all(db=db, skip=skip, limit=limit)
    

    @staticmethod
    async def get_task_for_action(
        db: AsyncSession, 
        task_id: int, 
        user: User
    ) -> Task:
        """
        Fetch a task and verify if the user has permission to modify it.
        - OWNER role: Can modify ANY task
        - MEMBER role: Can only modify their own tasks
        """
        task = await TaskRepository.get_by_id(db, id=task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        require_task_modification(user, task)
            
        return task
    
    @staticmethod
    async def change_task_owner(
        db: AsyncSession,
        task_id: int,
        new_owner_id: int,
        current_user: User
    ) -> Task:
        """
        Change the owner of a task.
        Only users with OWNER role can perform this action.
        
        Validations:
        - Current user must have OWNER role
        - Task must exist
        - New owner must exist
        - New owner must be active
        """
        # Verify current user has OWNER role
        require_owner_role(current_user)
        
        # Verificar que la tarea existe
        task = await TaskRepository.get_by_id(db, id=task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verificar que el nuevo propietario existe
        new_owner = await UserRepository.get_by_id(db, id=new_owner_id)
        if not new_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New owner not found"
            )
        
        # Verificar que el nuevo propietario está activo
        if not new_owner.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign task to inactive user"
            )
        
        # Actualizar el propietario de la tarea
        task.owner_id = new_owner_id
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # Cargar la relación owner
        await db.refresh(task, ["owner"])
        
        return task