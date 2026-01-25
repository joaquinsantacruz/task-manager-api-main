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
    
    Args:
        v: The datetime value to validate
        
    Returns:
        The validated datetime value (timezone-aware)
        
    Raises:
        ValueError: If the date is in the past
    """
    if v is not None:
        # Make both timezone-aware for comparison
        now = datetime.now(timezone.utc)
        due_date = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        
        if due_date < now:
            raise ValueError('Due date cannot be in the past')
    return v
