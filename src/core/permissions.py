"""
Centralized authorization and permission checking.

This module provides reusable permission checking functions to avoid
duplicating authorization logic across the application.
"""

from fastapi import HTTPException, status
from src.models.user import User, UserRole
from src.models.task import Task
from src.models.comment import Comment
from src.models.notification import Notification


def require_owner_role(user: User) -> None:
    """
    Verify that the user has the OWNER role.
    
    Args:
        user: The user to check
        
    Raises:
        HTTPException: 403 if user doesn't have OWNER role
    """
    if user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires OWNER role"
        )


def can_user_access_task(user: User, task: Task) -> bool:
    """
    Check if a user can access/view a task.
    
    Rules:
    - Task owner can access their own tasks
    - Users with OWNER role can access any task
    
    Args:
        user: The user attempting to access
        task: The task being accessed
        
    Returns:
        True if user can access the task, False otherwise
    """
    return task.owner_id == user.id or user.role == UserRole.OWNER


def require_task_access(user: User, task: Task) -> None:
    """
    Verify that a user can access a task, raise exception if not.
    
    Args:
        user: The user attempting to access
        task: The task being accessed
        
    Raises:
        HTTPException: 403 if user cannot access the task
    """
    if not can_user_access_task(user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )


def can_user_modify_task(user: User, task: Task) -> bool:
    """
    Check if a user can modify a task.
    
    Rules:
    - Task owner can modify their own tasks
    - Users with OWNER role can modify any task
    
    Args:
        user: The user attempting to modify
        task: The task being modified
        
    Returns:
        True if user can modify the task, False otherwise
    """
    return task.owner_id == user.id or user.role == UserRole.OWNER


def require_task_modification(user: User, task: Task) -> None:
    """
    Verify that a user can modify a task, raise exception if not.
    
    Note: Returns 404 instead of 403 to avoid leaking information
    about task existence to unauthorized users.
    
    Args:
        user: The user attempting to modify
        task: The task being modified
        
    Raises:
        HTTPException: 404 if user cannot modify the task
    """
    if not can_user_modify_task(user, task):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


def can_user_modify_comment(user: User, comment: Comment) -> bool:
    """
    Check if a user can modify (edit) a comment.
    
    Rules:
    - Only the comment author can edit their comment
    
    Args:
        user: The user attempting to modify
        comment: The comment being modified
        
    Returns:
        True if user can modify the comment, False otherwise
    """
    return comment.author_id == user.id


def require_comment_modification(user: User, comment: Comment) -> None:
    """
    Verify that a user can modify a comment, raise exception if not.
    
    Args:
        user: The user attempting to modify
        comment: The comment being modified
        
    Raises:
        HTTPException: 403 if user cannot modify the comment
    """
    if not can_user_modify_comment(user, comment):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this comment"
        )


def can_user_delete_comment(user: User, comment: Comment) -> bool:
    """
    Check if a user can delete a comment.
    
    Rules:
    - Comment author can delete their own comment
    - Users with OWNER role can delete any comment (moderation)
    
    Args:
        user: The user attempting to delete
        comment: The comment being deleted
        
    Returns:
        True if user can delete the comment, False otherwise
    """
    return comment.author_id == user.id or user.role == UserRole.OWNER


def require_comment_deletion(user: User, comment: Comment) -> None:
    """
    Verify that a user can delete a comment, raise exception if not.
    
    Args:
        user: The user attempting to delete
        comment: The comment being deleted
        
    Raises:
        HTTPException: 403 if user cannot delete the comment
    """
    if not can_user_delete_comment(user, comment):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment"
        )


def can_user_access_notification(user: User, notification: Notification) -> bool:
    """
    Check if a user can access a notification.
    
    Rules:
    - Only the notification owner can access it
    
    Args:
        user: The user attempting to access
        notification: The notification being accessed
        
    Returns:
        True if user can access the notification, False otherwise
    """
    return notification.user_id == user.id


def require_notification_access(user: User, notification: Notification) -> None:
    """
    Verify that a user can access a notification, raise exception if not.
    
    Args:
        user: The user attempting to access
        notification: The notification being accessed
        
    Raises:
        HTTPException: 403 if user cannot access the notification
    """
    if not can_user_access_notification(user, notification):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )
