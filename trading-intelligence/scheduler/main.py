"""Scheduler entry point — manages periodic tasks."""

from __future__ import annotations

import asyncio

from backend.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger("scheduler")


async def main() -> None:
    """Run the scheduler.

    The scheduler manages:
    - News collection intervals (every 5 min)
    - Market data polling (every 1 min)
    - Macro data updates (every 1 hour)
    - Indicator calculations (every 5 min after market data)
    - Prediction evaluation (1h, 4h, 24h, 7d)
    - Daily reports
    - Backup (daily)
    """
    logger.info("scheduler_starting")

    # TODO: Implement APScheduler-based task scheduling
    # For now, this is a placeholder

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

    logger.info("scheduler_stopped")


if __name__ == "__main__":
    asyncio.run(main())
