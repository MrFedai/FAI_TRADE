"""Binance public API source adapter."""

from __future__ import annotations

from typing import Any

import httpx

from workers.base_source import BaseSource, SourceResult
from backend.logging_config import get_logger

logger = get_logger("workers.market.binance")


class BinanceSource(BaseSource):
    """Binance public market data source.

    Uses public endpoints — no API key required.
    Reference: https://developers.binance.com/en/docs/binance-spot-api
    """

    name = "binance"
    source_type = "public_api"
    source_priority = 1
    rate_limit_per_min = 1200  # Binance weight-based limit

    BASE_URL = "https://api.binance.com"
    KLINES_ENDPOINT = "/api/v3/klines"
    TICKER_ENDPOINT = "/api/v3/ticker/24hr"
    AVG_PRICE_ENDPOINT = "/api/v3/avgPrice"

    async def fetch_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
    ) -> SourceResult:
        """Fetch candlestick data.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT").
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w).
            limit: Number of candles (max 1000).

        Returns:
            SourceResult with klines data.
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}{self.KLINES_ENDPOINT}",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        # Parse klines into structured format
        klines = []
        for k in data:
            klines.append({
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
            })

        self.update_last_fetch()
        return SourceResult(
            source=self.name,
            timestamp=DataTimestamp.now(),
            data={
                "symbol": symbol,
                "interval": interval,
                "klines": klines,
            },
            confidence=1.0,
            source_priority=self.source_priority,
        )

    async def fetch_ticker(self, symbol: str) -> SourceResult:
        """Fetch 24hr ticker statistics.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT").

        Returns:
            SourceResult with ticker data.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.BASE_URL}{self.TICKER_ENDPOINT}",
                params={"symbol": symbol},
            )
            response.raise_for_status()
            data = response.json()

        self.update_last_fetch()
        return SourceResult(
            source=self.name,
            timestamp=DataTimestamp.now(),
            data={
                "symbol": data["symbol"],
                "last_price": float(data["lastPrice"]),
                "price_change": float(data["priceChange"]),
                "price_change_pct": float(data["priceChangePercent"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
                "volume_24h": float(data["volume"]),
                "quote_volume_24h": float(data["quoteVolume"]),
            },
            confidence=1.0,
            source_priority=self.source_priority,
        )

    async def fetch(self, **kwargs: Any) -> SourceResult:
        """Default fetch — fetches ticker for BTCUSDT."""
        symbol = kwargs.get("symbol", "BTCUSDT")
        return await self.fetch_ticker(symbol)

    async def health_check(self) -> bool:
        """Check if Binance API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}{self.TICKER_ENDPOINT}",
                    params={"symbol": "BTCUSDT"},
                )
                return response.status_code == 200
        except Exception:
            return False


# Helper for timestamps (avoid circular imports)
from datetime import datetime, timezone
DataTimestamp = type("DataTimestamp", (), {"now": staticmethod(lambda: datetime.now(timezone.utc))})()
