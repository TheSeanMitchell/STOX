"""
core/fetcher.py — Robust multi-source fetcher with rate limiting and retry logic.
"""

import time
import random
import hashlib
import logging
import feedparser
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from core.cache import Cache

log = logging.getLogger("stox.fetcher")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; STOXBot/1.0; "
        "+https://github.com/yourusername/stox)"
    )
}
REQUEST_TIMEOUT = 15
MAX_WORKERS = 8
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0


def fetch_all_sources(
    sources: List[Dict],
    cache: Cache,
    max_workers: int = MAX_WORKERS
) -> List[Dict]:
    """
    Fetch all sources in parallel. Each source dict must have:
      { "url": str, "type": "rss"|"json"|"html", "tier": int, "label": str }
    Returns flat list of raw item dicts.
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_fetch_one, src, cache): src
            for src in sources
        }
        for future in as_completed(futures):
            src = futures[future]
            try:
                items = future.result()
                results.extend(items)
                log.debug(f"[{src['label']}] → {len(items)} items")
            except Exception as e:
                log.warning(f"[{src['label']}] fetch failed: {e}")
    return results


def _fetch_one(source: Dict, cache: Cache) -> List[Dict]:
    url = source["url"]
    tier = source.get("tier", 2)
    label = source.get("label", url)
    src_type = source.get("type", "rss")

    # Check cache
    cached = cache.get(url)
    if cached is not None:
        log.debug(f"[{label}] cache hit")
        return cached

    for attempt in range(MAX_RETRIES):
        try:
            if src_type == "rss":
                items = _parse_rss(url, tier, label)
            elif src_type == "json":
                items = _parse_json(url, tier, label, source.get("json_path", []))
            else:
                items = []

            cache.set(url, items, ttl=3600)
            return items

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                sleep_time = RETRY_BACKOFF ** attempt + random.uniform(0, 1)
                log.debug(f"[{label}] retry {attempt + 1} after {sleep_time:.1f}s")
                time.sleep(sleep_time)
            else:
                raise e
    return []


def _parse_rss(url: str, tier: int, label: str) -> List[Dict]:
    feed = feedparser.parse(
        url,
        request_headers=HEADERS,
        agent=HEADERS["User-Agent"]
    )
    items = []
    for entry in feed.entries[:50]:
        published = _parse_date(entry)
        items.append({
            "raw_title": entry.get("title", ""),
            "raw_summary": entry.get("summary", entry.get("description", "")),
            "url": entry.get("link", ""),
            "source_label": label,
            "source_url": url,
            "tier": tier,
            "published": published,
            "type": "rss",
        })
    return items


def _parse_json(url: str, tier: int, label: str, json_path: List) -> List[Dict]:
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    # Navigate nested path
    for key in json_path:
        if isinstance(data, dict):
            data = data.get(key, [])
        elif isinstance(data, list):
            break
    items = []
    if not isinstance(data, list):
        return []
    for entry in data[:50]:
        items.append({
            "raw_title": entry.get("headline", entry.get("title", "")),
            "raw_summary": entry.get("summary", entry.get("description", "")),
            "url": entry.get("url", entry.get("link", "")),
            "source_label": label,
            "source_url": url,
            "tier": tier,
            "published": entry.get("datetime", entry.get("publishedAt", "")),
            "type": "json",
        })
    return items


def _parse_date(entry) -> str:
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            t = entry.published_parsed
            return datetime(
                t.tm_year, t.tm_mon, t.tm_mday,
                t.tm_hour, t.tm_min, t.tm_sec,
                tzinfo=timezone.utc
            ).isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()
