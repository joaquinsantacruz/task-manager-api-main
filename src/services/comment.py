from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.user import User
from src.schemas.comment import CommentCreate, CommentUpdate
from src.repositories.comment import CommentRepository
from src.repositories.task import TaskRepository
from src.core.permissions import require_task_access, require_comment_modification, require_comment_deletion
from src.core.constants import DEFAULT_PAGE_SIZE


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
        """
        # Verify task exists
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify permissions using centralized function
        require_task_access(current_user, task)
        
        return await CommentRepository.get_by_task(db, task_id, skip, limit)
    
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        task_id: int,
        comment_data: CommentCreate,
        current_user: User
    ) -> Comment:
        """
        Create a comment on a task.
        Only task owner or users with OWNER role can comment.
        """
        # Verify task exists
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify permissions using centralized function
        require_task_access(current_user, task)
        
        return await CommentRepository.create(db, task_id, current_user.id, comment_data)
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: User
    ) -> Comment:
        """
        Update a comment.
        Only the comment author can edit it.
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify permissions using centralized function
        require_comment_modification(current_user, comment)
        
        return await CommentRepository.update(db, comment, comment_data)
    
    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: int,
        current_user: User
    ) -> None:
        """
        Delete a comment.
        Only the comment author or users with OWNER role can delete it.
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify permissions using centralized function
        require_comment_deletion(current_user, comment)
        
        await CommentRepository.delete(db, comment)
