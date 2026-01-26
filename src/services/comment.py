from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.errors import ERROR_TASK_NOT_FOUND, ERROR_COMMENT_NOT_FOUND
from src.core.permissions import require_task_access, require_comment_modification, require_comment_deletion
from src.core.logger import get_logger
from src.models.comment import Comment
from src.models.user import User
from src.repositories.comment import CommentRepository
from src.repositories.task import TaskRepository
from src.schemas.comment import CommentCreate, CommentUpdate

logger = get_logger(__name__)


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
        Create a new comment on a task.
        
        This method allows authorized users to add comments to tasks for
        collaboration and tracking purposes. Comments are timestamped and
        attributed to the user who created them.
        
        Permission Rules:
            - Task owner can always comment on their own tasks
            - Users with OWNER role can comment on any task
            - MEMBER role users can only comment on tasks they own
        
        Args:
            db: Async database session for executing queries
            task_id: Unique identifier of the task to comment on
            comment_in: CommentCreate schema containing:
                - content (str): The comment text/message (required)
            current_user: The authenticated user creating the comment
        
        Returns:
            Comment: The newly created comment object with:
                - id: Auto-generated comment ID
                - content: The comment text
                - author_id: ID of the user who created it (current_user.id)
                - task_id: ID of the associated task
                - created_at: Timestamp when comment was created
                - updated_at: Initially same as created_at
        
        Raises:
            HTTPException 404: If task with the given ID doesn't exist
            HTTPException 403: If current user doesn't have access to the task
        
        Security:
            - Uses centralized permission validation (require_task_access)
            - Author is automatically set to current_user (cannot be spoofed)
            - Comment ownership is immutable after creation
        
        Note:
            - Comments cannot be created on non-existent tasks
            - Comment content should be validated at schema level for length/format
            - Comments are associated with tasks, not with specific task versions
        """
        # Verify task exists
        task = await TaskRepository.get_by_id(db, task_id)
        if not task:
            logger.warning(f"Attempt to create comment on non-existent task {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_TASK_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_task_access(current_user, task)
        
        try:
            logger.info(f"User {current_user.id} creating comment on task {task_id}")
            comment = await CommentRepository.create(db, task_id, current_user.id, comment_in)
            logger.info(f"Comment {comment.id} created successfully on task {task_id}")
            return comment
        except Exception as e:
            logger.error(f"Error creating comment on task {task_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_in: CommentUpdate,
        current_user: User
    ) -> Comment:
        """
        Update the content of an existing comment.
        
        This method allows comment authors to edit their own comments.
        Only the original author can modify a comment, ensuring content
        integrity and accountability.
        
        Permission Rules:
            - Only the comment author (author_id = current_user.id) can edit
            - OWNER role users cannot edit comments they didn't create
            - Task owner cannot edit comments from other users
        
        Args:
            db: Async database session for executing queries
            comment_id: Unique identifier of the comment to update
            comment_in: CommentUpdate schema containing:
                - content (str, optional): New comment text to replace existing
            current_user: The authenticated user attempting to update the comment
        
        Returns:
            Comment: The updated comment object with:
                - All original fields preserved
                - content: Updated to new value if provided
                - updated_at: Timestamp updated to current time
                - created_at: Remains unchanged (original creation time)
        
        Raises:
            HTTPException 404: If comment with the given ID doesn't exist
            HTTPException 403: If current user is not the comment author
        
        Security:
            - Strict author-only modification policy
            - Uses centralized permission validation (require_comment_modification)
            - Cannot change comment ownership or associated task
        
        Note:
            - updated_at timestamp is automatically updated
            - Only content field can be modified
            - No edit history is maintained (consider adding if needed)
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            logger.warning(f"Comment {comment_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COMMENT_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_comment_modification(current_user, comment)
        
        try:
            logger.info(f"User {current_user.id} updating comment {comment_id}")
            updated_comment = await CommentRepository.update(db, comment, comment_in)
            logger.info(f"Comment {comment_id} updated successfully")
            return updated_comment
        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: int,
        current_user: User
    ) -> None:
        """
        Permanently delete a comment from the system.
        
        This method removes a comment from the database. Deletion is allowed
        for the comment author and users with OWNER role, providing moderation
        capabilities while respecting content ownership.
        
        Permission Rules:
            - Comment author can always delete their own comments
            - Users with OWNER role can delete any comment (moderation)
            - MEMBER role users can only delete comments they authored
        
        Args:
            db: Async database session for executing queries
            comment_id: Unique identifier of the comment to delete
            current_user: The authenticated user attempting to delete the comment
        
        Returns:
            None
        
        Raises:
            HTTPException 404: If comment with the given ID doesn't exist
            HTTPException 403: If current user doesn't have permission to delete
        
        Security:
            - Uses centralized permission validation (require_comment_deletion)
            - OWNER role provides moderation capabilities
            - Author can always remove their own content
        
        Note:
            - This is a hard delete operation (not soft delete)
            - Deleted comments cannot be recovered
            - No notification is sent to task owner or comment author
            - Consider implementing soft delete if comment history is needed
        """
        comment = await CommentRepository.get_by_id(db, comment_id)
        if not comment:
            logger.warning(f"Comment {comment_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_COMMENT_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_comment_deletion(current_user, comment)
        
        try:
            logger.info(f"User {current_user.id} deleting comment {comment_id}")
            await CommentRepository.delete(db, comment)
            logger.info(f"Comment {comment_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {str(e)}", exc_info=True)
            raise
