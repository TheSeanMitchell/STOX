"""
sources/google_news.py — Dynamic Google News RSS query builder.
Generates rotating search queries to discover trending financial news.
"""

import random
import urllib.parse
from typing import List, Dict

# Core query templates
QUERY_TEMPLATES = [
    "{ticker} earnings",
    "{ticker} forecast",
    "{ticker} upgrade downgrade",
    "{ticker} acquisition merger",
    "{ticker} revenue growth",
    "{ticker} lawsuit investigation",
    "{ticker} guidance raised",
    "{ticker} layoffs restructuring",
    "{ticker} product launch",
    "{ticker} partnership deal",
]

MACRO_QUERIES = [
    "stock market rally",
    "stock market crash",
    "Federal Reserve interest rates",
    "inflation CPI report",
    "GDP growth forecast",
    "earnings season results",
    "IPO launch 2025",
    "crypto regulation",
    "tech stocks outlook",
    "oil price OPEC",
    "gold price forecast",
    "housing market outlook",
    "S&P 500 forecast",
    "NASDAQ outlook",
    "bond yield curve",
    "recession probability",
    "AI stocks investment",
    "semiconductor shortage",
    "China economy market",
    "emerging markets",
]

ROTATING_TICKERS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL",
    "JPM", "BAC", "GS", "V", "MA", "PYPL",
    "AMD", "INTC", "QCOM", "TSM",
    "NFLX", "DIS", "UBER",
    "COIN", "MSTR",
    "SPY", "QQQ",
    "GLD", "USO",
    "BTC", "ETH",
    "PANW", "CRWD", "NET", "SNOW", "PLTR",
]


def build_google_news_queries(
    n_ticker_queries: int = 30,
    include_macro: bool = True,
) -> List[Dict]:
    """
    Generate a set of Google News RSS source dicts for dynamic discovery.
    Returns list of source configs compatible with fetch_all_sources().
    """
    sources = []

    # Macro queries (all of them)
    if include_macro:
        for query in MACRO_QUERIES:
            sources.append(_make_gn_source(query, tier=2, label=f"GNews: {query[:40]}"))

    # Rotating ticker queries (random sample each run = exploration)
    tickers = random.sample(ROTATING_TICKERS, min(n_ticker_queries, len(ROTATING_TICKERS)))
    for ticker in tickers:
        template = random.choice(QUERY_TEMPLATES)
        query = template.format(ticker=ticker)
        sources.append(_make_gn_source(query, tier=2, label=f"GNews: {query}"))

    return sources


def _make_gn_source(query: str, tier: int = 2, label: str = None) -> Dict:
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    return {
        "label": label or f"GNews:{query[:30]}",
        "url": url,
        "type": "rss",
        "tier": tier,
    }
