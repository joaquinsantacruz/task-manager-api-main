"""
Health check endpoint.

Provides API health status and basic system information.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Annotated

from src.api.deps import get_db
from src.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Health check endpoint.
    
    Returns:
        - status: API health status
        - timestamp: Current server time (UTC)
        - version: API version
        - database: Database connection status
    """
    # Check database connectivity
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "database": db_status,
    }
