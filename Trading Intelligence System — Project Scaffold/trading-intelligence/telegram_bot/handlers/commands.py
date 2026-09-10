"""Telegram bot command handlers."""

from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("telegram_bot.handlers")

# Backend API URL (internal Docker network or Tailscale)
BACKEND_URL = settings.tailscale_ip if settings.tailscale_ip != "127.0.0.1" else "localhost"
BACKEND_API = f"http://{BACKEND_URL}:8000" if settings.tailscale_ip == "127.0.0.1" else f"http://backend:8000"


def _is_allowed(update: Update) -> bool:
    """Check if the user is authorized to use the bot."""
    if not settings.allowed_user_ids:
        return True  # No restriction if not configured
    user_id = update.effective_user.id if update.effective_user else 0
    return user_id in settings.allowed_user_ids


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not _is_allowed(update):
        return

    name = update.effective_user.first_name if update.effective_user else "User"
    await update.message.reply_text(
        f"Merhaba {name}.\n\n"
        "Personal Trading Intelligence System\n\n"
        "Komutlar:\n"
        "/news - Son haberler\n"
        "/macro - Yaklasan makro olaylar\n"
        "/market BTC - Market raporu\n"
        "/signals - Aktif sinyaller\n"
        "/report - Gunluk rapor\n"
        "/status - Sistem durumu\n\n"
        "Bu sistem karar destek amaclidir. Ticari kararlar size aittir."
    )


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /news command."""
    if not _is_allowed(update):
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BACKEND_API}/api/news?limit=10")
            if resp.status_code == 200:
                items = resp.json()
                if not items:
                    await update.message.reply_text("Su an yeni haber yok.")
                    return
                # Format news
                lines = ["Son Haberler:\n"]
                for item in items[:10]:
                    lines.append(f"- [{item.get('title', '?')}]({item.get('url', '#')})")
                    lines.append(f"  Kaynak: {item.get('source_name', '?')} | "
                                 f"Oncelik: {item.get('importance_score', '?')}/10\n")
                await update.message.reply_text(
                    "\n".join(lines),
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            else:
                await update.message.reply_text("Haberler alinamadi. Backend calismiyor olabilir.")
    except httpx.ConnectError:
        await update.message.reply_text("Backend'e erisilemedi. /status ile kontrol edin.")
    except Exception as e:
        logger.error("news_command_error", error=str(e))
        await update.message.reply_text("Bir hata olustu.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    if not _is_allowed(update):
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{BACKEND_API}/health")
            if resp.status_code == 200:
                await update.message.reply_text("Sistem durumu: CALISIYOR\nBackend: OK")
            else:
                await update.message.reply_text("Sistem durumu: SORUNLU\nBackend yanit vermiyor.")
    except httpx.ConnectError:
        await update.message.reply_text("Sistem durumu: OFFLINE\nBackend'e erisilemiyor.")
    except Exception as e:
        logger.error("status_command_error", error=str(e))
        await update.message.reply_text("Sistem durumu kontrol edilemedi.")


async def cmd_market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /market command."""
    if not _is_allowed(update):
        return

    if not context.args:
        await update.message.reply_text("Kullanim: /market BTC")
        return

    asset = context.args[0].upper()
    await update.message.reply_text(f"{asset} icin market raporu hazirlaniyor... (yakinda)")


async def cmd_macro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /macro command."""
    if not _is_allowed(update):
        return

    await update.message.reply_text("Makro veriler hazirlaniyor... (yakinda)")


async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /signals command."""
    if not _is_allowed(update):
        return

    await update.message.reply_text("Sinyaller hazirlaniyor... (yakinda)")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /report command."""
    if not _is_allowed(update):
        return

    await update.message.reply_text("Gunluk rapor hazirlaniyor... (yakinda)")


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command."""
    if not _is_allowed(update):
        return

    await update.message.reply_text("Saglik kontrolu yapiliyor... (yakinda)")


async def setup_handlers(token: str) -> None:
    """Set up and start the Telegram bot."""
    app = ApplicationBuilder().token(token).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("market", cmd_market))
    app.add_handler(CommandHandler("macro", cmd_macro))
    app.add_handler(CommandHandler("signals", cmd_signals))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("health", cmd_health))

    logger.info("telegram_handlers_registered")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep running
    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
