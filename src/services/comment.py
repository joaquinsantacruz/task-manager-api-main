from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.user import User, UserRole
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
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
    ) -> List[CommentResponse]:
        """
        Obtiene los comentarios de una tarea.
        Solo el owner de la tarea o usuarios OWNER pueden ver los comentarios.
        """
        # Verificar que la tarea existe
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Verificar permisos: solo el owner de la tarea o un OWNER puede ver los comentarios
        if task.owner_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver los comentarios de esta tarea"
            )
        
        comments = await CommentRepository.get_by_task(db, task_id, skip, limit)
        
        # Convertir a response incluyendo el email del autor
        return [
            CommentResponse(
                id=comment.id,
                content=comment.content,
                task_id=comment.task_id,
                author_id=comment.author_id,
                author_email=comment.author.email if comment.author else None,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            )
            for comment in comments
        ]
    
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        task_id: int,
        comment_data: CommentCreate,
        current_user: User
    ) -> CommentResponse:
        """
        Crea un comentario en una tarea.
        Solo el owner de la tarea o usuarios OWNER pueden comentar.
        """
        # Verificar que la tarea existe
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Verificar permisos: solo el owner de la tarea o un OWNER puede comentar
        if task.owner_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para comentar en esta tarea"
            )
        
        comment = await CommentRepository.create(db, task_id, current_user.id, comment_data)
        
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author_email=comment.author.email if comment.author else None,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: User
    ) -> CommentResponse:
        """
        Actualiza un comentario.
        Solo el autor del comentario puede editarlo.
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )
        
        # Solo el autor puede editar su comentario
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para editar este comentario"
            )
        
        updated_comment = await CommentRepository.update(db, comment, comment_data)
        
        return CommentResponse(
            id=updated_comment.id,
            content=updated_comment.content,
            task_id=updated_comment.task_id,
            author_id=updated_comment.author_id,
            author_email=updated_comment.author.email if updated_comment.author else None,
            created_at=updated_comment.created_at,
            updated_at=updated_comment.updated_at
        )
    
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
                detail="Comentario no encontrado"
            )
        
        # Solo el autor o un OWNER pueden eliminar el comentario
        if comment.author_id != current_user.id and current_user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este comentario"
            )
        
        await CommentRepository.delete(db, comment)
