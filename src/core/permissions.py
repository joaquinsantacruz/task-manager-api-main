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
from src.core.errors import (
    ERROR_OWNER_ROLE_REQUIRED,
    ERROR_NO_TASK_ACCESS,
    ERROR_TASK_NOT_FOUND,
    ERROR_COMMENT_NOT_FOUND,
    ERROR_NOTIFICATION_NOT_FOUND
)

def require_owner_role(user: User) -> None:
    """
    Verify that the user has the OWNER role, raising an exception if not.
    
    This is a strict role check used to protect administrative operations
    that should only be accessible to users with OWNER privileges.
    
    Args:
        user: The user object to check for OWNER role
        
    Raises:
        HTTPException 403: If user.role is not UserRole.OWNER
    
    Usage:
        Use this function at the start of operations that require OWNER privileges,
        such as:
        - Creating new users
        - Changing task ownership
        - Accessing all tasks in the system
        - Administrative endpoints
    
    Example:
        >>> require_owner_role(current_user)
        >>> # Code here only executes if current_user is OWNER
    """
    if user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_OWNER_ROLE_REQUIRED
        )


def can_user_access_task(user: User, task: Task) -> bool:
    """
    Check if a user has permission to view/access a task.
    
    This function implements the read permission logic for tasks,
    determining whether a user should be able to see task details.
    
    Permission Rules:
        - Task owner (owner_id == user.id): Can access their own tasks
        - OWNER role users: Can access any task in the system
        - MEMBER role users: Can only access tasks they own
    
    Args:
        user: The user attempting to access the task
        task: The task being accessed
        
    Returns:
        bool: True if user has permission to access the task, False otherwise
    
    Usage:
        Use this for read-only operations like:
        - Viewing task details
        - Reading task comments
        - Checking task status
    
    Note:
        - This is for read access; use can_user_modify_task for write operations
        - Returns boolean (does not raise exceptions)
        - Combine with require_task_access for automatic exception handling
    """
    return task.owner_id == user.id or user.role == UserRole.OWNER


def require_task_access(user: User, task: Task) -> None:
    """
    Verify that a user has permission to access a task, raising an exception if not.
    
    This function enforces read permissions for tasks by checking if the user
    is either the task owner or has OWNER role. It raises a 403 Forbidden
    exception if access is denied.
    
    Args:
        user: The user attempting to access the task
        task: The task being accessed
        
    Raises:
        HTTPException 403: If user cannot access the task (not owner and not OWNER role)
    
    Usage:
        Call this function before allowing read operations on a task:
        - Viewing task details
        - Listing task comments
        - Checking task notifications
    
    Security:
        - Returns 403 Forbidden (not 404) to indicate permission denial
        - Error message is generic to avoid information disclosure
    
    Example:
        >>> require_task_access(current_user, task)
        >>> # If we reach here, user has permission
        >>> return task
    """
    if not can_user_access_task(user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_NO_TASK_ACCESS
        )


def can_user_modify_task(user: User, task: Task) -> bool:
    """
    Check if a user has permission to modify (update/delete) a task.
    
    This function implements the write permission logic for tasks,
    determining whether a user can make changes to a task.
    
    Permission Rules:
        - Task owner (owner_id == user.id): Can modify their own tasks
        - OWNER role users: Can modify any task in the system
        - MEMBER role users: Can only modify tasks they own
    
    Args:
        user: The user attempting to modify the task
        task: The task being modified
        
    Returns:
        bool: True if user has permission to modify the task, False otherwise
    
    Usage:
        Use this for write operations like:
        - Updating task title, description, status, due date
        - Deleting tasks
        - Changing task properties
    
    Note:
        - This is for write access (read access uses can_user_access_task)
        - Returns boolean (does not raise exceptions)
        - Combine with require_task_modification for automatic exception handling
        - Task ownership changes have separate permission logic (OWNER role only)
    """
    return task.owner_id == user.id or user.role == UserRole.OWNER


def require_task_modification(user: User, task: Task) -> None:
    """
    Verify that a user has permission to modify a task, raising an exception if not.
    
    This function enforces write permissions for tasks by checking if the user
    is either the task owner or has OWNER role. It raises a 404 Not Found
    exception (not 403) to prevent information disclosure.
    
    Args:
        user: The user attempting to modify the task
        task: The task being modified
        
    Raises:
        HTTPException 404: If user cannot modify the task (appears as "task not found")
    
    Security Consideration:
        Returns 404 instead of 403 to avoid leaking information about task existence
        to unauthorized users. This prevents attackers from enumerating task IDs.
    
    Usage:
        Call this function before allowing write operations on a task:
        - Updating task fields
        - Deleting tasks
        - Changing task status
    
    Example:
        >>> require_task_modification(current_user, task)
        >>> # If we reach here, user can modify the task
        >>> task.status = new_status
    """
    if not can_user_modify_task(user, task):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_TASK_NOT_FOUND
        )


def can_user_modify_comment(user: User, comment: Comment) -> bool:
    """
    Check if a user has permission to edit a comment.
    
    This function implements a strict author-only edit policy for comments,
    ensuring content integrity and accountability.
    
    Permission Rules:
        - Comment author only: Only the user who created the comment can edit it
        - OWNER role users: Cannot edit comments they didn't create
        - Task owners: Cannot edit comments from other users
    
    Args:
        user: The user attempting to modify the comment
        comment: The comment being modified
        
    Returns:
        bool: True if user is the comment author, False otherwise
    
    Usage:
        Use this before allowing edit operations on comments:
        - Updating comment content
        - Correcting typos
    
    Note:
        - More restrictive than deletion (deletion allows OWNER role)
        - Preserves comment authorship integrity
        - Returns boolean (does not raise exceptions)
        - Combine with require_comment_modification for automatic exception handling
    """
    return comment.author_id == user.id


def require_comment_modification(user: User, comment: Comment) -> None:
    """
    Verify that a user has permission to modify a comment, raising an exception if not.
    
    This function enforces the author-only edit policy for comments.
    It raises a 404 exception (not 403) to prevent information disclosure.
    
    Args:
        user: The user attempting to modify the comment
        comment: The comment being modified
        
    Raises:
        HTTPException 404: If user is not the comment author (appears as "comment not found")
    
    Security Consideration:
        Returns 404 instead of 403 to avoid leaking information about comment existence
        to unauthorized users.
    
    Usage:
        Call this function before allowing edit operations on comments:
        - Updating comment content
    
    Example:
        >>> require_comment_modification(current_user, comment)
        >>> # If we reach here, user is the comment author
        >>> comment.content = new_content
    """
    if not can_user_modify_comment(user, comment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_COMMENT_NOT_FOUND
        )


def can_user_delete_comment(user: User, comment: Comment) -> bool:
    """
    Check if a user has permission to delete a comment.
    
    This function implements a more permissive deletion policy compared to
    editing, allowing OWNER role users to moderate comments.
    
    Permission Rules:
        - Comment author: Can always delete their own comments
        - OWNER role users: Can delete any comment (moderation capability)
        - MEMBER role users: Can only delete comments they authored
    
    Args:
        user: The user attempting to delete the comment
        comment: The comment being deleted
        
    Returns:
        bool: True if user can delete the comment, False otherwise
    
    Usage:
        Use this before allowing deletion of comments:
        - Removing inappropriate content (moderation)
        - User-initiated comment removal
    
    Note:
        - Less restrictive than editing (allows OWNER role moderation)
        - Returns boolean (does not raise exceptions)
        - Combine with require_comment_deletion for automatic exception handling
        - Enables content moderation by administrators
    """
    return comment.author_id == user.id or user.role == UserRole.OWNER


def require_comment_deletion(user: User, comment: Comment) -> None:
    """
    Verify that a user has permission to delete a comment, raising an exception if not.
    
    This function enforces deletion permissions for comments, allowing both
    authors and OWNER role users to delete comments.
    
    Args:
        user: The user attempting to delete the comment
        comment: The comment being deleted
        
    Raises:
        HTTPException 404: If user cannot delete the comment (appears as "comment not found")
    
    Security Consideration:
        Returns 404 instead of 403 to avoid leaking information about comment existence
        to unauthorized users.
    
    Usage:
        Call this function before allowing deletion of comments:
        - User-initiated deletion
        - Admin/moderator content removal
    
    Example:
        >>> require_comment_deletion(current_user, comment)
        >>> # If we reach here, user can delete (either author or OWNER)
        >>> await CommentRepository.delete(db, comment)
    """
    if not can_user_delete_comment(user, comment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_COMMENT_NOT_FOUND
        )


def can_user_access_notification(user: User, notification: Notification) -> bool:
    """
    Check if a user has permission to access a notification.
    
    This function implements strict privacy for notifications, ensuring
    users can only access their own notifications.
    
    Permission Rules:
        - Notification owner only: User can only access notifications sent to them
        - OWNER role: Cannot access other users' notifications (privacy protection)
        - No cross-user notification access allowed
    
    Args:
        user: The user attempting to access the notification
        notification: The notification being accessed
        
    Returns:
        bool: True if notification belongs to the user, False otherwise
    
    Usage:
        Use this before allowing operations on notifications:
        - Viewing notification details
        - Marking notifications as read
        - Deleting notifications
    
    Note:
        - Strictest permission model (even OWNER role cannot access others' notifications)
        - Protects user privacy
        - Returns boolean (does not raise exceptions)
        - Combine with require_notification_access for automatic exception handling
    """
    return notification.user_id == user.id


def require_notification_access(user: User, notification: Notification) -> None:
    """
    Verify that a user has permission to access a notification, raising an exception if not.
    
    This function enforces strict privacy for notifications by ensuring only
    the notification owner can access it.
    
    Args:
        user: The user attempting to access the notification
        notification: The notification being accessed
        
    Raises:
        HTTPException 404: If user is not the notification owner (appears as "notification not found")
    
    Security Consideration:
        Returns 404 instead of 403 to avoid leaking information about notification
        existence to unauthorized users. This prevents notification enumeration.
    
    Usage:
        Call this function before allowing any operation on a notification:
        - Viewing notification details
        - Marking as read
        - Deleting notification
    
    Privacy:
        Even OWNER role users cannot access notifications belonging to other users,
        ensuring maximum privacy for notification content.
    
    Example:
        >>> require_notification_access(current_user, notification)
        >>> # If we reach here, notification belongs to current_user
        >>> notification.is_read = True
    """
    if not can_user_access_notification(user, notification):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_NOTIFICATION_NOT_FOUND
        )
