"""
Centralized error messages and HTTP error handling.

This module provides consistent error messages across the application
to improve maintainability and user experience.
"""

# ============================================================================
# AUTHENTICATION & AUTHORIZATION ERRORS
# ============================================================================

ERROR_INVALID_CREDENTIALS = "Could not validate credentials"
ERROR_INCORRECT_EMAIL_OR_PASSWORD = "Incorrect email or password"
ERROR_INACTIVE_USER = "Inactive user"
ERROR_INSUFFICIENT_PERMISSIONS = "Insufficient permissions. OWNER role required."
ERROR_OWNER_ROLE_REQUIRED = "This action requires OWNER role"

# ============================================================================
# RESOURCE NOT FOUND ERRORS
# ============================================================================

ERROR_TASK_NOT_FOUND = "Task not found"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_COMMENT_NOT_FOUND = "Comment not found"
ERROR_NOTIFICATION_NOT_FOUND = "Notification not found"

# ============================================================================
# PERMISSION ERRORS
# ============================================================================

ERROR_NO_TASK_ACCESS = "You do not have permission to access this task"
ERROR_NO_TASK_MODIFICATION = "You do not have permission to modify this task"
ERROR_NO_COMMENT_MODIFICATION = "You do not have permission to modify this comment"
ERROR_NO_COMMENT_DELETION = "You do not have permission to delete this comment"
ERROR_NO_NOTIFICATION_ACCESS = "You do not have permission to access this notification"

# ============================================================================
# BUSINESS LOGIC ERRORS
# ============================================================================

ERROR_INVALID_USER_DATA = "Invalid user data"
ERROR_INACTIVE_USER_CREATE_TASK = "Inactive users cannot create tasks"
ERROR_ASSIGN_INACTIVE_USER = "Cannot assign task to inactive user"
ERROR_NEW_OWNER_NOT_FOUND = "New owner not found"
