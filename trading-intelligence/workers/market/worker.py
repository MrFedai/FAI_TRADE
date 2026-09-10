"""Market data worker — fetches crypto/stock/commodity prices."""

from __future__ import annotations

from workers.base_worker import BaseWorker
from workers.market.binance_source import BinanceSource
from backend.logging_config import get_logger

logger = get_logger("workers.market")


class MarketWorker(BaseWorker):
    """Background worker that fetches market price data."""

    worker_name = "market"
    poll_interval = 60  # 1 minute

    # Crypto pairs on Binance
    CRYPTO_SYMBOLS = {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT",
        "SOL": "SOLUSDT",
        "XRP": "XRPUSDT",
    }

    def __init__(self, poll_interval: int | None = None):
        super().__init__(poll_interval)
        self.binance = BinanceSource()

    async def run_once(self) -> None:
        """Fetch market data for all watchlist assets."""
        logger.info("market_worker_iteration_start")

        for asset, symbol in self.CRYPTO_SYMBOLS.items():
            try:
                result = await self.binance.fetch_ticker(symbol)
                logger.info(
                    "market_data_fetched",
                    asset=asset,
                    price=result.data.get("last_price"),
                    source=result.source,
                )
                # TODO: Store in market_prices table
            except Exception as e:
                logger.error(
                    "market_data_error",
                    asset=asset,
                    error=str(e),
                )

        logger.info("market_worker_iteration_done")

    async def health_check(self) -> bool:
        """Check if Binance API is reachable."""
        return await self.binance.health_check()
