"""Base source adapter — all data source adapters inherit from this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class SourceResult(BaseModel):
    """Standardized result from a data source."""

    source: str
    timestamp: datetime
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any]
    confidence: float = 0.5
    source_priority: int = 1  # 1=primary, 2=secondary, 3=social


class BaseSource(ABC):
    """Abstract base class for all data source adapters.

    Each adapter (BinanceSource, FREDSource, NewsRSSSource, etc.)
    must implement this interface.
    """

    name: str = "base"
    source_type: str = "unknown"
    source_priority: int = 1
    rate_limit_per_min: int = 60
    _last_fetch: datetime | None = None

    @abstractmethod
    async def fetch(self, **kwargs: Any) -> SourceResult:
        """Fetch data from the source.

        Returns:
            SourceResult with retrieved data.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the source is reachable.

        Returns:
            True if the source is available.
        """
        pass

    @property
    def last_fetch(self) -> datetime | None:
        """Get the last fetch timestamp."""
        return self._last_fetch

    def update_last_fetch(self) -> None:
        """Update the last fetch timestamp."""
        self._last_fetch = datetime.now(timezone.utc)
