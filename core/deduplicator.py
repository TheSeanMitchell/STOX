"""
core/deduplicator.py — Multi-strategy deduplication: exact + fuzzy fingerprinting.
"""

import re
import logging
from typing import List, Dict, Set
from difflib import SequenceMatcher

log = logging.getLogger("stox.dedup")

SIMILARITY_THRESHOLD = 0.85
MAX_SEEN_FINGERPRINTS = 50_000


def deduplicate(items: List[Dict], cache) -> List[Dict]:
    """
    Remove duplicates using:
    1. Exact fingerprint match (MD5 of title+url)
    2. Fuzzy title similarity
    3. Persistent seen-set via cache
    """
    seen_fingerprints: Set[str] = set(cache.get("dedup:fingerprints") or [])
    seen_titles: List[str] = []
    unique = []

    for item in items:
        fp = item.get("fingerprint", "")

        # 1. Exact fingerprint check
        if fp and fp in seen_fingerprints:
            continue

        # 2. Fuzzy title dedup
        title = item.get("title", "")
        title_norm = _normalize_title(title)
        if _is_similar_to_seen(title_norm, seen_titles):
            continue

        # Accept item
        unique.append(item)
        if fp:
            seen_fingerprints.add(fp)
        seen_titles.append(title_norm)

    # Trim seen set to max size
    if len(seen_fingerprints) > MAX_SEEN_FINGERPRINTS:
        seen_fingerprints = set(list(seen_fingerprints)[-MAX_SEEN_FINGERPRINTS:])

    cache.set("dedup:fingerprints", list(seen_fingerprints), ttl=86400)
    log.debug(f"Dedup: {len(items)} → {len(unique)} unique items")
    return unique


def _normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^a-z0-9 ]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def _is_similar_to_seen(title: str, seen: List[str]) -> bool:
    if not title:
        return False
    # Only check recent items for performance
    for seen_title in seen[-500:]:
        ratio = SequenceMatcher(None, title, seen_title).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            return True
    return False
