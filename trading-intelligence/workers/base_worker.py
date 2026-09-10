"""Base worker class for all background workers."""

from __future__ import annotations

import asyncio
import signal
from abc import ABC, abstractmethod
from typing import Any

from backend.config import settings
from backend.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger("workers.base")


class BaseWorker(ABC):
    """Abstract base class for all background workers.

    Workers run continuously and perform scheduled data collection tasks.
    Each worker type (news, market, macro) implements this interface.
    """

    worker_name: str = "base"
    poll_interval: int = 60  # seconds between runs

    def __init__(self, poll_interval: int | None = None):
        if poll_interval is not None:
            self.poll_interval = poll_interval
        self._running = False
        self._shutdown_event = asyncio.Event()

    @abstractmethod
    async def run_once(self) -> None:
        """Run one iteration of the worker's task.

        This method is called at each poll interval.
        Implementations should handle their own errors.
        """
        pass

    async def start(self) -> None:
        """Start the worker loop."""
        self._running = True
        logger.info("worker_starting", worker=self.worker_name)

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._signal_shutdown)
            except NotImplementedError:
                pass  # Not supported on all platforms

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(
                    "worker_iteration_error",
                    worker=self.worker_name,
                    error=str(e),
                )

            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.poll_interval,
                )
            except asyncio.TimeoutError:
                continue  # Normal timeout, continue loop

        logger.info("worker_stopped", worker=self.worker_name)

    def _signal_shutdown(self) -> None:
        """Signal the worker to shut down."""
        logger.info("worker_shutdown_signal", worker=self.worker_name)
        self._running = False
        self._shutdown_event.set()

    def stop(self) -> None:
        """Stop the worker."""
        self._running = False
        self._shutdown_event.set()
