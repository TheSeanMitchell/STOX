"""
engine/scorer.py — Aggregate per-article sentiment into per-asset scores.
Weights by source tier, recency, and source diversity.
"""

import math
import logging
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List

log = logging.getLogger("stox.scorer")

RECENCY_HALF_LIFE_HOURS = 12.0  # Score halves every 12 hours
MIN_ARTICLES_FOR_CONFIDENCE = 3


def aggregate_scores(scored_items: List[Dict]) -> Dict[str, Dict]:
    """
    Group scored articles by asset_tag and aggregate into per-asset intelligence.
    Returns { ticker: AssetScore }
    """
    asset_buckets: Dict[str, List[Dict]] = defaultdict(list)

    for item in scored_items:
        for ticker in item.get("asset_tags", []):
            asset_buckets[ticker].append(item)

    aggregated = {}
    for ticker, items in asset_buckets.items():
        if not items:
            continue
        aggregated[ticker] = _compute_asset_score(ticker, items)

    return aggregated


def _compute_asset_score(ticker: str, items: List[Dict]) -> Dict:
    now = datetime.now(timezone.utc)
    total_weight = 0.0
    weighted_sentiment = 0.0
    sources_seen = set()
    tiers_seen = set()
    signal_counts = {"STRONGLY_POSITIVE": 0, "POSITIVE": 0,
                     "NEUTRAL": 0, "NEGATIVE": 0, "STRONGLY_NEGATIVE": 0}
    recent_headlines = []

    for item in items:
        # Recency decay
        age_h = _age_hours(item.get("timestamp"), now)
        recency = _recency_weight(age_h)

        # Combined weight
        w = item.get("weight", 0.5) * recency
        score = item.get("sentiment_score", 0.0)

        weighted_sentiment += score * w
        total_weight += w

        source = item.get("source", "unknown")
        tier = item.get("tier", 2)
        sources_seen.add(source)
        tiers_seen.add(tier)

        label = item.get("sentiment_label", "NEUTRAL")
        signal_counts[label] = signal_counts.get(label, 0) + 1

        if len(recent_headlines) < 5:
            recent_headlines.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": source,
                "timestamp": item.get("timestamp", ""),
                "sentiment_label": label,
                "sentiment_score": item.get("sentiment_score", 0.0),
            })

    final_score = (weighted_sentiment / total_weight) if total_weight > 0 else 0.0
    confidence = _compute_confidence(len(items), len(sources_seen), len(tiers_seen))

    return {
        "ticker": ticker,
        "sentiment_score": round(final_score, 4),
        "confidence": round(confidence, 3),
        "article_count": len(items),
        "source_count": len(sources_seen),
        "tier_count": len(tiers_seen),
        "signal_distribution": signal_counts,
        "recent_headlines": recent_headlines,
        "sources": sorted(sources_seen),
    }


def _recency_weight(age_hours: float) -> float:
    """Exponential decay: weight = e^(-λ * t), where λ = ln(2) / half_life."""
    lam = math.log(2) / RECENCY_HALF_LIFE_HOURS
    return math.exp(-lam * age_hours)


def _age_hours(timestamp: str, now: datetime) -> float:
    if not timestamp:
        return 24.0
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        diff = (now - ts).total_seconds() / 3600
        return max(0.0, diff)
    except Exception:
        return 24.0


def _compute_confidence(n_articles: int, n_sources: int, n_tiers: int) -> float:
    """
    Confidence: 0.0 → 1.0
    Based on article volume, source diversity, and tier diversity.
    """
    article_factor = min(1.0, math.log1p(n_articles) / math.log1p(20))
    source_factor = min(1.0, n_sources / 5.0)
    tier_factor = n_tiers / 3.0
    return (article_factor * 0.5 + source_factor * 0.35 + tier_factor * 0.15)
