"""Worker entry point — dispatches to the correct worker based on WORKER_TYPE."""

from __future__ import annotations

import asyncio
import os
import sys

from backend.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger("workers.main")


async def main() -> None:
    """Start the appropriate worker based on WORKER_TYPE environment variable."""
    worker_type = os.environ.get("WORKER_TYPE", "").lower()

    if not worker_type:
        logger.error("worker_type_not_set")
        print("ERROR: WORKER_TYPE environment variable not set.")
        print("Valid values: news, market, macro")
        sys.exit(1)

    logger.info("worker_dispatching", worker_type=worker_type)

    if worker_type == "news":
        from workers.news.worker import NewsWorker
        worker = NewsWorker()
    elif worker_type == "market":
        from workers.market.worker import MarketWorker
        worker = MarketWorker()
    elif worker_type == "macro":
        from workers.macro.worker import MacroWorker
        worker = MacroWorker()
    else:
        logger.error("worker_type_unknown", worker_type=worker_type)
        print(f"ERROR: Unknown WORKER_TYPE: {worker_type}")
        print("Valid values: news, market, macro")
        sys.exit(1)

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
