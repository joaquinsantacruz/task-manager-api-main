from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentUpdate
from src.core.constants import DEFAULT_PAGE_SIZE


class CommentRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """
        Retrieve a comment by its unique identifier with author relationship loaded.
        
        This method fetches a single comment and eagerly loads the associated
        author (User) relationship to avoid N+1 query problems.
        
        Args:
            db: Async database session for executing queries
            comment_id: Unique identifier of the comment to retrieve
        
        Returns:
            Optional[Comment]: Comment object with author relationship loaded if found,
                              None if no comment exists with the given ID
        
        Note:
            - Eagerly loads author relationship via joinedload
            - Does not load task relationship (only author)
            - Returns None rather than raising exception if not found
            - Does not verify comment ownership or permissions
        """
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == comment_id)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_by_task(db: AsyncSession, task_id: int, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> List[Comment]:
        """
        Retrieve all comments for a specific task with pagination.
        
        This method returns all comments associated with a task, ordered by
        creation date (newest first) with author relationships eagerly loaded.
        
        Args:
            db: Async database session for executing queries
            task_id: ID of the task whose comments to retrieve
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of comments to return (default: DEFAULT_PAGE_SIZE)
        
        Returns:
            List[Comment]: List of comment objects with author relationships loaded,
                          ordered by created_at DESC (newest first).
                          Returns empty list if task has no comments.
        
        Note:
            - Results are ordered by created_at in descending order (newest first)
            - Author relationship is eagerly loaded for each comment
            - Does not verify if task exists (returns empty list for invalid task_id)
            - Task relationship is NOT loaded (only author)
        """
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
        """
        Create a new comment on a task.
        
        This method creates a comment with the provided content, commits it to
        the database, and returns the fully initialized comment object with
        author relationship loaded.
        
        Args:
            db: Async database session for executing queries
            task_id: ID of the task being commented on
            author_id: ID of the user creating the comment
            comment_in: CommentCreate schema containing comment data (content)
        
        Returns:
            Comment: Newly created comment object with:
                - Auto-generated ID
                - content from comment_in
                - task_id and author_id as specified
                - Author relationship eagerly loaded
                - Timestamps (created_at, updated_at) auto-populated
        
        Note:
            - Commits transaction immediately
            - Performs additional query to eager load author relationship
            - Does not validate if task_id or author_id exist (foreign key constraints apply)
            - Task relationship is not loaded (only author)
        """
        db_comment = Comment(
            content=comment_in.content,
            task_id=task_id,
            author_id=author_id
        )
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        
        # Load the author relationship
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == db_comment.id)
        )
        return result.one()
    
    @staticmethod
    async def update(db: AsyncSession, comment: Comment, comment_in: CommentUpdate) -> Comment:
        """
        Update the content of an existing comment.
        
        This method updates the comment's content field, commits the change,
        and returns the refreshed comment object with author relationship loaded.
        
        Args:
            db: Async database session for executing queries
            comment: Comment object to update (already fetched from database)
            comment_in: CommentUpdate schema containing new content
        
        Returns:
            Comment: Updated comment object with:
                - content updated to new value
                - updated_at timestamp automatically refreshed
                - Author relationship eagerly loaded
                - created_at preserved (original creation time)
        
        Note:
            - Only updates the content field
            - Commits transaction immediately
            - Performs additional query to eager load author relationship
            - Does not validate comment ownership (must be checked before calling)
            - updated_at is automatically updated by database
        """
        comment.content = comment_in.content
        await db.commit()
        await db.refresh(comment)
        
        # Load the author relationship
        result = await db.scalars(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.id == comment.id)
        )
        return result.one()
    
    @staticmethod
    async def delete(db: AsyncSession, comment: Comment) -> None:
        """
        Permanently delete a comment from the database.
        
        This method performs a hard delete, completely removing the comment
        from the system.
        
        Args:
            db: Async database session for executing queries
            comment: Comment object to delete (already fetched from database)
        
        Returns:
            None
        
        Note:
            - This is a hard delete (not soft delete)
            - Commits transaction immediately
            - Cannot be undone after commit
            - Does not validate comment ownership or permissions (must be checked before calling)
            - Does not affect the associated task
        """
        await db.delete(comment)
        await db.commit()
