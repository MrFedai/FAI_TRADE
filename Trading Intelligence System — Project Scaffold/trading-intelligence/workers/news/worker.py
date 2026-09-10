"""News worker — collects and processes RSS news feeds."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import feedparser

from workers.base_worker import BaseWorker
from workers.news.rss_sources import RSS_SOURCES
from backend.logging_config import get_logger

logger = get_logger("workers.news")


class NewsWorker(BaseWorker):
    """Background worker that fetches RSS news feeds, deduplicates, and stores them."""

    worker_name = "news"
    poll_interval = 300  # 5 minutes

    def __init__(self, poll_interval: int | None = None):
        super().__init__(poll_interval)

    async def run_once(self) -> None:
        """Fetch all RSS feeds and process new articles."""
        logger.info("news_worker_iteration_start")

        total_fetched = 0
        total_new = 0
        total_duplicate = 0

        for source in RSS_SOURCES:
            try:
                articles = await self._fetch_feed(source)
                total_fetched += len(articles)

                for article in articles:
                    dedup_hash = self._compute_dedup_hash(article)
                    # TODO: Check if dedup_hash already exists in DB
                    # TODO: If new, store in news table
                    # For now, just count
                    total_new += 1

            except Exception as e:
                logger.error(
                    "news_source_error",
                    source=source["name"],
                    error=str(e),
                )

        logger.info(
            "news_worker_iteration_done",
            fetched=total_fetched,
            new=total_new,
            duplicates=total_duplicate,
        )

    async def _fetch_feed(self, source: dict) -> list[dict]:
        """Fetch and parse an RSS feed.

        Args:
            source: Dict with name, url, category.

        Returns:
            List of parsed articles.
        """
        feed = feedparser.parse(source["url"])
        articles = []

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()
            if not title or not url:
                continue

            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                pub_dt = datetime.now(timezone.utc)

            articles.append({
                "title": title,
                "url": url,
                "source_name": source["name"],
                "category": source["category"],
                "published_at": pub_dt.isoformat(),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "summary": entry.get("summary", ""),
            })

        return articles

    @staticmethod
    def _compute_dedup_hash(article: dict) -> str:
        """Compute a deduplication hash for an article.

        Uses URL as the primary dedup key.
        Falls back to title hash if URL is empty.
        """
        key = article.get("url", "") or article.get("title", "")
        return hashlib.sha256(key.encode()).hexdigest()

    async def health_check(self) -> bool:
        """Check if at least one RSS source is reachable."""
        # TODO: Implement actual health check
        return True
