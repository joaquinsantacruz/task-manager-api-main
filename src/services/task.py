from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.errors import (
    ERROR_INACTIVE_USER_CREATE_TASK,
    ERROR_TASK_NOT_FOUND,
    ERROR_NEW_OWNER_NOT_FOUND,
    ERROR_ASSIGN_INACTIVE_USER
)
from src.core.permissions import require_owner_role, require_task_modification
from src.models.task import Task
from src.models.user import User, UserRole
from src.repositories.task import TaskRepository
from src.repositories.user import UserRepository
from src.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_data: TaskCreate,
        current_user: User
    ) -> Task:
        """
        Create a new task.
        
        Validations:
        - User must be active to create tasks
        
        The task will be automatically assigned to the current user.
        """
        # Verify that the user is active
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_INACTIVE_USER_CREATE_TASK
            )
        
        return await TaskRepository.create(db, task_data, current_user.id)
    
    @staticmethod
    async def get_tasks_for_user(
        db: AsyncSession, 
        user: User, 
        skip: int = 0, 
        limit: int = DEFAULT_PAGE_SIZE,
        only_mine: bool = False
    ) -> List[Task]:
        """
        Get tasks for a user.
        
        - OWNER role: Returns all tasks unless only_mine is True
        - MEMBER role: Returns only user's own tasks
        
        Args:
            db: Database session
            user: Current authenticated user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            only_mine: If True, return only user's own tasks
        
        Returns:
            List of Task objects
        """
        if only_mine or user.role != UserRole.OWNER:
            return await TaskRepository.get_multi_by_owner(
                db=db, owner_id=user.id, skip=skip, limit=limit
            )
        
        return await TaskRepository.get_all(db=db, skip=skip, limit=limit)
    
    @staticmethod
    async def get_task_by_id_for_user(
        db: AsyncSession,
        task_id: int,
        user: User
    ) -> Task:
        """
        Get a task by ID for a specific user.
        Only returns the task if the user owns it.
        
        Args:
            db: Database session
            task_id: ID of the task to retrieve
            user: Current user
            
        Returns:
            The task if found and owned by user
            
        Raises:
            HTTPException: 404 if task not found or not owned by user
        """
        task = await TaskRepository.get_by_id_and_owner(
            db=db, id=task_id, owner_id=user.id
        )
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TASK_NOT_FOUND)
        return task
    

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_TASK_NOT_FOUND)

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
        
        # Verify that the task exists
        task = await TaskRepository.get_by_id(db, id=task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_TASK_NOT_FOUND
            )
        
        # Verify that the new owner exists
        new_owner = await UserRepository.get_by_id(db, id=new_owner_id)
        if not new_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_NEW_OWNER_NOT_FOUND
            )
        
        # Verify that the new owner is active
        if not new_owner.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_ASSIGN_INACTIVE_USER
            )
        
        # Update the task owner using repository
        return await TaskRepository.change_owner(db, task, new_owner_id)
    
    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        task_in: TaskUpdate,
        current_user: User
    ) -> Task:
        """
        Update a task.
        
        Validations:
        - Task must exist
        - User must have permission to modify the task:
          * OWNER role: Can modify any task
          * MEMBER role: Can only modify their own tasks
        
        Args:
            db: Database session
            task_id: ID of the task to update
            task_in: TaskUpdate schema with fields to update
            current_user: Current authenticated user
        
        Returns:
            Updated Task object
        """
        task = await TaskService.get_task_for_action(db, task_id, current_user)
        return await TaskRepository.update(db=db, db_obj=task, obj_in=task_in)

    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: int,
        current_user: User
    ) -> None:
        """
        Delete a task.
        
        Validations:
        - Task must exist
        - User must have permission to modify the task:
          * OWNER role: Can delete any task
          * MEMBER role: Can only delete their own tasks
        
        Args:
            db: Database session
            task_id: ID of the task to delete
            current_user: Current authenticated user
        """
        task = await TaskService.get_task_for_action(db, task_id, current_user)
        await TaskRepository.delete(db=db, db_obj=task)

