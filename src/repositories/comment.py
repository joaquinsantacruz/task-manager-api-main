from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """Obtiene un comentario por su ID, incluyendo el autor."""
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == comment_id)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_by_task(db: AsyncSession, task_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtiene todos los comentarios de una tarea, ordenados por fecha de creación."""
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())
    
    @staticmethod
    async def create(db: AsyncSession, task_id: int, author_id: int, comment_in: CommentCreate) -> Comment:
        """Crea un nuevo comentario en una tarea."""
        db_comment = Comment(
            content=comment_in.content,
            task_id=task_id,
            author_id=author_id
        )
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        
        # Cargar la relación del autor
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == db_comment.id)
        )
        return result.one()
    
    @staticmethod
    async def update(db: AsyncSession, comment: Comment, comment_in: CommentUpdate) -> Comment:
        """Actualiza el contenido de un comentario."""
        comment.content = comment_in.content
        await db.commit()
        await db.refresh(comment)
        
        # Cargar la relación del autor
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == comment.id)
        )
        return result.one()
    
    @staticmethod
    async def delete(db: AsyncSession, comment: Comment) -> None:
        """Elimina un comentario."""
        await db.delete(comment)
        await db.commit()
