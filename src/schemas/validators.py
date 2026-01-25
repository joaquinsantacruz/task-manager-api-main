"""
Common Pydantic validators for reuse across schemas.

This module provides reusable field validators to avoid code duplication
and ensure consistent validation logic across different schemas.
"""

from datetime import datetime, timezone
from typing import Optional


def validate_due_date_not_past(v: Optional[datetime]) -> Optional[datetime]:
    """
    Validate that a due_date is not in the past.
    
    Compares only the date part (ignoring time) to allow setting due dates
    for the current day regardless of the current time.
    
    Args:
        v: The datetime value to validate
        
    Returns:
        The validated datetime value (timezone-aware)
        
    Raises:
        ValueError: If the date is in the past (before today)
    """
    if v is not None:
        # Make both timezone-aware for comparison
        now = datetime.now(timezone.utc)
        due_date = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        
        # Compare only the date part (year, month, day)
        # This allows setting a due date for today regardless of the current time
        if due_date.date() < now.date():
            raise ValueError('Due date cannot be in the past')
    return v
