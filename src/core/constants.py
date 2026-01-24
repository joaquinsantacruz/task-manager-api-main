"""
Application-wide constants and business rules.

This module centralizes magic numbers and hardcoded values to improve
maintainability and make business rules explicit.
"""

# ============================================================================
# PAGINATION DEFAULTS
# ============================================================================
DEFAULT_PAGE_SIZE = 100
"""Default number of items returned per page in list endpoints."""

MAX_PAGE_SIZE = 1000
"""Maximum allowed page size to prevent excessive database queries."""


# ============================================================================
# STRING LENGTH CONSTRAINTS
# ============================================================================

# Task constraints
TASK_TITLE_MIN_LENGTH = 1
TASK_TITLE_MAX_LENGTH = 100
"""Maximum length for task titles. Matches database column constraint."""

TASK_DESCRIPTION_MAX_LENGTH = 5000
"""Maximum length for task descriptions to prevent abuse."""


# User constraints
USER_EMAIL_MAX_LENGTH = 255
"""Standard maximum length for email addresses."""

USER_PASSWORD_MIN_LENGTH = 8
"""Minimum password length for security."""

USER_PASSWORD_MAX_LENGTH = 100
"""Maximum password length (before hashing)."""


# Comment constraints
COMMENT_CONTENT_MIN_LENGTH = 1
COMMENT_CONTENT_MAX_LENGTH = 5000
"""Maximum length for comment content."""


# Notification constraints
NOTIFICATION_MESSAGE_MAX_LENGTH = 500
"""Maximum length for notification messages."""
