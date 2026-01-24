from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.user import User, UserRole
from src.schemas.comment import CommentCreate, CommentUpdate
from src.repositories.comment import CommentRepository
from src.repositories.task import TaskRepository


class CommentService:
    
    @staticmethod
    async def get_task_comments(
        db: AsyncSession,
        task_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """
        Obtiene los comentarios de una tarea.
        Solo el owner de la tarea o usuarios OWNER pueden ver los comentarios.
        """
        # Verificar que la tarea existe
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verificar permisos: solo el owner de la tarea o un OWNER puede ver los comentarios
        if task.owner_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view comments on this task"
            )
        
        return await CommentRepository.get_by_task(db, task_id, skip, limit)
    
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        task_id: int,
        comment_data: CommentCreate,
        current_user: User
    ) -> Comment:
        """
        Crea un comentario en una tarea.
        Solo el owner de la tarea o usuarios OWNER pueden comentar.
        """
        # Verificar que la tarea existe
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verificar permisos: solo el owner de la tarea o un OWNER puede comentar
        if task.owner_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to comment on this task"
            )
        
        return await CommentRepository.create(db, task_id, current_user.id, comment_data)
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: User
    ) -> Comment:
        """
        Actualiza un comentario.
        Solo el autor del comentario puede editarlo.
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Solo el autor puede editar su comentario
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this comment"
            )
        
        return await CommentRepository.update(db, comment, comment_data)
    
    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: int,
        current_user: User
    ) -> None:
        """
        Elimina un comentario.
        Solo el autor del comentario o un OWNER pueden eliminarlo.
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Solo el autor o un OWNER pueden eliminar el comentario
        if comment.author_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment"
            )
        
        await CommentRepository.delete(db, comment)
