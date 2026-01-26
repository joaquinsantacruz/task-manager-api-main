"""
Tests for health check endpoint.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings


class TestHealthCheck:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy_status(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that health check returns healthy status when database is available."""
        response = await client.get(f"{settings.API_V1_STR}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["database"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_check_no_authentication_required(
        self, client: AsyncClient
    ):
        """Test that health check does not require authentication."""
        response = await client.get(f"{settings.API_V1_STR}/health")
        
        assert response.status_code == 200
        assert "status" in response.json()

    @pytest.mark.asyncio
    async def test_health_check_timestamp_is_valid_iso_format(
        self, client: AsyncClient
    ):
        """Test that health check returns valid ISO timestamp."""
        from datetime import datetime
        
        response = await client.get(f"{settings.API_V1_STR}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be able to parse as ISO format datetime
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert timestamp is not None
