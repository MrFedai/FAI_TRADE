"""RSS news source definitions — candidate feeds to be verified in Phase 2."""

# These are candidate RSS feeds. URLs must be verified in Phase 2.
# If a feed is unreachable or returns errors, it should be disabled.

RSS_SOURCES: list[dict] = [
    # Crypto news
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "category": "crypto"},
    {"name": "CoinTelegraph", "url": "https://cointelegraph.com/rss", "category": "crypto"},
    # Macro / Fed
    {"name": "Fed Press Releases", "url": "https://www.federalreserve.gov/feeds/press_all.xml", "category": "macro"},
    # Stock IR feeds
    {"name": "NVDA IR", "url": "https://investor.nvidia.com/rss/news-releases.xml", "category": "stock"},
    {"name": "TSLA IR", "url": "https://ir.tesla.com/rss/news-releases.xml", "category": "stock"},
    {"name": "AAPL IR", "url": "https://investor.apple.com/rss/news.rss", "category": "stock"},
    {"name": "MSFT IR", "url": "https://www.microsoft.com/en-us/investor/rss-feed", "category": "stock"},
]
