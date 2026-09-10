"""Telegram bot entry point."""

from __future__ import annotations

import asyncio

from telegram_bot.handlers.commands import setup_handlers
from telegram_bot.health import run_health_server
from backend.config import settings
from backend.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger("telegram_bot")


async def main() -> None:
    """Start the Telegram bot."""
    if not settings.telegram_bot_token:
        logger.error("telegram_token_missing")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set. Get it from @BotFather.")

    logger.info("telegram_bot_starting")

    # Start health server in background
    health_task = asyncio.create_task(run_health_server(port=8001))

    try:
        await setup_handlers(settings.telegram_bot_token)
    except Exception as e:
        logger.error("telegram_bot_error", error=str(e))
        raise
    finally:
        health_task.cancel()
        try:
            await health_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
