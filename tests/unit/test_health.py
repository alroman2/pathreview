"""Reproduction tests for Issue #68.

The /health endpoint exposes a `safety_events_last_hour` field but currently
hardcodes it to 0 (see api/routes/health.py:78). It never queries
safety.monitoring.SafetyMonitor, so real safety activity stored in Redis is
never surfaced to operators. These tests document that bug and are expected to
fail until the endpoint is wired to SafetyMonitor.

Issue: https://github.com/ascherj/pathreview/issues/68
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from api.routes.health import health_check
from safety.monitoring import SafetyMonitor


@pytest.mark.unit
class TestHealthSafetyEventsRepro:
    """Reproduce Issue #68: safety_events_last_hour is hardcoded to 0."""

    @pytest.fixture
    def mock_db(self):
        """Async mock DB session that satisfies `await db.execute(...)`."""
        db = MagicMock()
        db.execute = AsyncMock()
        return db

    @pytest.mark.asyncio
    async def test_safety_events_last_hour_reflects_safety_monitor(self, mock_db):
        """The endpoint should surface the count SafetyMonitor reports.

        SafetyMonitor.get_event_count is stubbed to return 7 events for the
        last hour. Because health_check hardcodes the field to 0 instead of
        consulting SafetyMonitor, this assertion fails -> reproduces #68.
        """
        with patch.object(SafetyMonitor, "get_event_count", return_value=7), \
                patch("redis.Redis"), \
                patch("core.config.settings") as mock_settings:
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379
            mock_settings.vector_db_url = "http://localhost:8001"
            result = await health_check(db=mock_db)

        assert result["safety_events_last_hour"] == 7