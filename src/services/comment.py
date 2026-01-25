from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.errors import ERROR_TASK_NOT_FOUND, ERROR_COMMENT_NOT_FOUND
from src.core.permissions import require_task_access, require_comment_modification, require_comment_deletion
from src.models.comment import Comment
from src.models.user import User
from src.repositories.comment import CommentRepository
from src.repositories.task import TaskRepository
from src.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    
    @staticmethod
    async def get_task_comments(
        db: AsyncSession,
        task_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_SIZE
    ) -> List[Comment]:
        """
        Get comments for a task.
        Only task owner or users with OWNER role can view comments.
        
        Args:
            db: Database session
            task_id: ID of the task to get comments for
            current_user: Current authenticated user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
        
        Returns:
            List of Comment objects
        """
        # Verify task exists
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_TASK_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_task_access(current_user, task)
        
        return await CommentRepository.get_by_task(db, task_id, skip, limit)
    
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        task_id: int,
        comment_in: CommentCreate,
        current_user: User
    ) -> Comment:
        """
        Create a comment on a task.
        Only task owner or users with OWNER role can comment.
        
        Args:
            db: Database session
            task_id: ID of the task to comment on
            comment_in: CommentCreate schema with comment data
            current_user: Current authenticated user
        
        Returns:
            Created Comment object
        """
        # Verify task exists
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_TASK_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_task_access(current_user, task)
        
        return await CommentRepository.create(db, task_id, current_user.id, comment_in)
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_in: CommentUpdate,
        current_user: User
    ) -> Comment:
        """
        Update a comment.
        Only the comment author can edit it.
        
        Args:
            db: Database session
            comment_id: ID of the comment to update
            comment_in: CommentUpdate schema with fields to update
            current_user: Current authenticated user
        
        Returns:
            Updated Comment object
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COMMENT_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_comment_modification(current_user, comment)
        
        return await CommentRepository.update(db, comment, comment_in)
    
    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: int,
        current_user: User
    ) -> None:
        """
        Delete a comment.
        Only the comment author or users with OWNER role can delete it.
        
        Args:
            db: Database session
            comment_id: ID of the comment to delete
            current_user: Current authenticated user
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COMMENT_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_comment_deletion(current_user, comment)
        
        await CommentRepository.delete(db, comment)
