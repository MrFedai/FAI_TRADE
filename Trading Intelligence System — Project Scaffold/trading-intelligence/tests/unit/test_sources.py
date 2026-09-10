"""Tests for the base source adapter pattern."""

import pytest

from workers.base_source import BaseSource, SourceResult


class DummySource(BaseSource):
    """Test implementation of BaseSource."""

    name = "dummy"
    source_type = "test"
    source_priority = 1

    async def fetch(self, **kwargs):
        return SourceResult(
            source=self.name,
            timestamp="2026-01-01T00:00:00Z",
            data={"test": True},
            confidence=0.9,
            source_priority=self.source_priority,
        )

    async def health_check(self) -> bool:
        return True


def test_source_result_creation() -> None:
    """SourceResult should be created with required fields."""
    result = SourceResult(
        source="test",
        timestamp="2026-01-01T00:00:00Z",
        data={"key": "value"},
    )
    assert result.source == "test"
    assert result.data == {"key": "value"}
    assert result.confidence == 0.5  # default
    assert result.source_priority == 1  # default


def test_dummy_source_name() -> None:
    """DummySource should have correct name."""
    source = DummySource()
    assert source.name == "dummy"
    assert source.source_priority == 1


def test_dummy_source_last_fetch() -> None:
    """last_fetch should be None initially and updated after fetch."""
    source = DummySource()
    assert source.last_fetch is None
    source.update_last_fetch()
    assert source.last_fetch is not None


@pytest.mark.asyncio
async def test_dummy_source_fetch() -> None:
    """fetch should return a SourceResult."""
    source = DummySource()
    result = await source.fetch()
    assert result.source == "dummy"
    assert result.data == {"test": True}
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_dummy_source_health() -> None:
    """health_check should return True."""
    source = DummySource()
    assert await source.health_check() is True
