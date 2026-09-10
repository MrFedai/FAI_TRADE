"""Simple health server for Docker healthchecks."""

from __future__ import annotations

import asyncio

from aiohttp import web


async def health_handler(request: web.Request) -> web.Response:
    """Simple health check endpoint."""
    return web.json_response({"status": "ok", "service": "telegram_bot"})


async def run_health_server(port: int = 8001) -> None:
    """Run a minimal HTTP health check server."""
    app = web.Application()
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    # Keep running
    while True:
        await asyncio.sleep(3600)
