from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException # Necesitarás importar esto

from src.models.user import User, UserRole
from src.models.task import Task
from src.repositories.task import TaskRepository

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
        Busca una tarea y verifica si el usuario tiene permiso para modificarla.
        - OWNER: Puede modificar CUALQUIER tarea.
        - MEMBER: Solo puede modificar las suyas.
        """
        task = await TaskRepository.get_by_id(db, id=task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.owner_id != user.id and user.role != UserRole.OWNER:
            raise HTTPException(status_code=404, detail="Task not found") 
            
        return task