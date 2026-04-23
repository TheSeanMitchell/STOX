"""
sources/sec_edgar.py — Fetch SEC EDGAR filings (S-1, 8-K, 10-K) via free RSS/ATOM.
No API key required.
"""

import re
import logging
import feedparser
from datetime import datetime, timezone
from typing import List, Dict

from core.cache import Cache

log = logging.getLogger("stox.edgar")

EDGAR_FEEDS = [
    {
        "label": "SEC S-1 (IPOs)",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=S-1&dateb=&owner=include&count=20&search_text=&output=atom",
        "filing_type": "S-1",
        "tier": 1,
    },
    {
        "label": "SEC 8-K (Material Events)",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&dateb=&owner=include&count=40&search_text=&output=atom",
        "filing_type": "8-K",
        "tier": 1,
    },
    {
        "label": "SEC 10-K (Annual Reports)",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=10-K&dateb=&owner=include&count=20&search_text=&output=atom",
        "filing_type": "10-K",
        "tier": 1,
    },
    {
        "label": "SEC DEF 14A (Proxy)",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=DEF+14A&dateb=&owner=include&count=20&search_text=&output=atom",
        "filing_type": "DEF14A",
        "tier": 2,
    },
]

FILING_SIGNALS = {
    "S-1": {"title_prefix": "IPO Filing", "sentiment_hint": 0.3},
    "8-K": {"title_prefix": "Material Event", "sentiment_hint": 0.0},
    "10-K": {"title_prefix": "Annual Report", "sentiment_hint": 0.0},
    "DEF14A": {"title_prefix": "Proxy Statement", "sentiment_hint": -0.1},
}


def fetch_edgar_filings(cache: Cache) -> List[Dict]:
    """Fetch and normalize SEC EDGAR filing feeds."""
    all_items = []
    for feed_cfg in EDGAR_FEEDS:
        try:
            cached = cache.get(f"edgar:{feed_cfg['filing_type']}")
            if cached:
                all_items.extend(cached)
                continue

            items = _fetch_feed(feed_cfg)
            cache.set(f"edgar:{feed_cfg['filing_type']}", items, ttl=3600)
            all_items.extend(items)
            log.debug(f"EDGAR {feed_cfg['filing_type']}: {len(items)} filings")
        except Exception as e:
            log.warning(f"EDGAR fetch failed for {feed_cfg['label']}: {e}")

    return all_items


def _fetch_feed(feed_cfg: Dict) -> List[Dict]:
    feed = feedparser.parse(feed_cfg["url"])
    filing_type = feed_cfg["filing_type"]
    hint = FILING_SIGNALS.get(filing_type, {})
    items = []

    for entry in feed.entries[:30]:
        title = entry.get("title", "")
        company = _extract_company(title)
        ticker = _guess_ticker(title)

        raw_title = f"[{hint.get('title_prefix', filing_type)}] {title}"

        items.append({
            "raw_title": raw_title,
            "raw_summary": (
                f"SEC filing type {filing_type} submitted. "
                f"Company: {company}. "
                + entry.get("summary", "")[:300]
            ),
            "url": entry.get("link", ""),
            "source_label": feed_cfg["label"],
            "source_url": feed_cfg["url"],
            "tier": feed_cfg["tier"],
            "published": datetime.now(timezone.utc).isoformat(),
            "type": "rss",
            "filing_type": filing_type,
            "edgar_company": company,
            "edgar_ticker_hint": ticker,
            "_sentiment_hint": hint.get("sentiment_hint", 0.0),
        })
    return items


def _extract_company(title: str) -> str:
    # Format: "CompanyName (TICKER) (filing_type)"
    match = re.match(r'^(.+?)\s+\(', title)
    return match.group(1).strip() if match else title[:50]


def _guess_ticker(title: str) -> str:
    match = re.search(r'\(([A-Z]{1,5})\)', title)
    return match.group(1) if match else ""
