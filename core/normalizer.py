"""
core/normalizer.py — Convert raw items into unified StoxItem schema.
"""

import re
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict

log = logging.getLogger("stox.normalizer")

# Common stock tickers (expandable)
KNOWN_TICKERS = {
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA",
    "AMD", "INTC", "NFLX", "DIS", "JPM", "BAC", "GS", "MS", "WMT",
    "TGT", "COST", "HD", "LOW", "CVX", "XOM", "COP", "BP", "AMGN",
    "PFE", "JNJ", "ABBV", "MRK", "LLY", "UNH", "V", "MA", "PYPL",
    "SQ", "COIN", "MSTR", "SPY", "QQQ", "IWM", "GLD", "SLV", "USO",
    "BTC", "ETH", "SOL", "ADA", "DOGE", "XRP", "BNB", "AVAX",
    "UBER", "LYFT", "ABNB", "SNAP", "TWTR", "RBLX", "HOOD", "RIVN",
    "LCID", "NIO", "BABA", "JD", "PDD", "TSM", "ASML", "SMCI",
    "ARM", "MRVL", "QCOM", "TXN", "LRCX", "KLAC", "AMAT", "CDNS",
    "PANW", "CRWD", "ZS", "OKTA", "NET", "SNOW", "DDOG", "MDB",
    "PLTR", "SOUN", "GME", "AMC", "BB", "BBBY",
}

COMPANY_TO_TICKER = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
    "alphabet": "GOOGL", "amazon": "AMZN", "meta": "META",
    "facebook": "META", "tesla": "TSLA", "nvidia": "NVDA",
    "netflix": "NFLX", "disney": "DIS", "walmart": "WMT",
    "jpmorgan": "JPM", "goldman sachs": "GS", "bitcoin": "BTC",
    "ethereum": "ETH", "solana": "SOL", "coinbase": "COIN",
    "palantir": "PLTR", "snowflake": "SNOW", "uber": "UBER",
    "airbnb": "ABNB", "paypal": "PYPL", "visa": "V",
    "mastercard": "MA", "pfizer": "PFE", "moderna": "MRNA",
}

TICKER_RE = re.compile(r'\b([A-Z]{1,5})\b')
CLEAN_RE = re.compile(r'<[^>]+>|&[a-z]+;')
WHITESPACE_RE = re.compile(r'\s+')


def normalize_items(raw_items: List[Dict]) -> List[Dict]:
    """Transform raw fetched items into the StoxItem schema."""
    normalized = []
    for raw in raw_items:
        try:
            item = _normalize_one(raw)
            if item:
                normalized.append(item)
        except Exception as e:
            log.debug(f"Normalize error: {e}")
    return normalized


def _normalize_one(raw: Dict) -> Dict:
    title = _clean_text(raw.get("raw_title", ""))
    summary = _clean_text(raw.get("raw_summary", ""))

    if not title:
        return None

    url = _clean_url(raw.get("url", ""))
    fingerprint = _fingerprint(title, url)

    asset_tags = _extract_assets(title + " " + summary)

    return {
        "title": title,
        "summary": summary[:500],
        "source": raw.get("source_label", "unknown"),
        "source_url": raw.get("source_url", ""),
        "url": url,
        "timestamp": _normalize_ts(raw.get("published", "")),
        "asset_tags": asset_tags,
        "tier": raw.get("tier", 2),
        "weight": _tier_weight(raw.get("tier", 2)),
        "fingerprint": fingerprint,
        "sentiment_score": 0.0,   # filled by sentiment engine
        "type": raw.get("type", "rss"),
    }


def _clean_text(text: str) -> str:
    text = CLEAN_RE.sub(" ", text or "")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def _clean_url(url: str) -> str:
    return url.split("?")[0].rstrip("/")


def _fingerprint(title: str, url: str) -> str:
    raw = f"{title[:80]}|{url}"
    return hashlib.md5(raw.encode()).hexdigest()


def _extract_assets(text: str) -> List[str]:
    text_upper = text.upper()
    text_lower = text.lower()

    found = set()

    # Direct ticker match
    for match in TICKER_RE.finditer(text_upper):
        ticker = match.group(1)
        if ticker in KNOWN_TICKERS:
            found.add(ticker)

    # Company name match
    for company, ticker in COMPANY_TO_TICKER.items():
        if company in text_lower:
            found.add(ticker)

    return sorted(found)


def _normalize_ts(ts) -> str:
    if not ts:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(ts, str) and ts:
        try:
            # Try ISO format
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat()
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat()


def _tier_weight(tier: int) -> float:
    return {1: 1.0, 2: 0.6, 3: 0.3}.get(tier, 0.5)
