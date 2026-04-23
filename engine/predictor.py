"""
engine/predictor.py — Rule-based prediction generator with confidence scoring.
Educational simulation only. NOT financial advice.
"""

import logging
from typing import Dict, List

log = logging.getLogger("stox.predictor")

# Signal thresholds
STRONG_BUY_THRESHOLD = 0.45
BUY_THRESHOLD = 0.20
SELL_THRESHOLD = -0.20
STRONG_SELL_THRESHOLD = -0.45

# Minimum confidence to emit a non-HOLD signal
MIN_CONFIDENCE = 0.20


def generate_predictions(
    aggregated: Dict[str, Dict],
    market_data: Dict[str, Dict],
) -> List[Dict]:
    """
    Generate prediction objects for all tracked assets.
    Returns list sorted by absolute |sentiment_score| descending.
    """
    predictions = []

    for ticker, asset in aggregated.items():
        score = asset["sentiment_score"]
        confidence = asset["confidence"]
        price_data = market_data.get(ticker) or market_data.get(f"{ticker}-USD", {})

        signal = _classify_signal(score, confidence)
        strength = _signal_strength(score)
        rationale = _build_rationale(asset, signal, price_data)

        predictions.append({
            "ticker": ticker,
            "signal": signal,
            "strength": strength,
            "confidence": round(confidence, 3),
            "sentiment_score": round(score, 4),
            "article_count": asset["article_count"],
            "source_count": asset["source_count"],
            "price": price_data.get("price"),
            "change_pct": price_data.get("change_pct"),
            "rationale": rationale,
            "recent_headlines": asset.get("recent_headlines", [])[:3],
            "signal_distribution": asset.get("signal_distribution", {}),
            "sources": asset.get("sources", []),
        })

    # Sort: high-confidence strong signals first
    predictions.sort(
        key=lambda p: abs(p["sentiment_score"]) * p["confidence"],
        reverse=True
    )
    return predictions


def _classify_signal(score: float, confidence: float) -> str:
    if confidence < MIN_CONFIDENCE:
        return "HOLD"
    if score >= STRONG_BUY_THRESHOLD:
        return "STRONG_BUY"
    elif score >= BUY_THRESHOLD:
        return "BUY"
    elif score <= STRONG_SELL_THRESHOLD:
        return "STRONG_SELL"
    elif score <= SELL_THRESHOLD:
        return "SELL"
    else:
        return "HOLD"


def _signal_strength(score: float) -> str:
    abs_score = abs(score)
    if abs_score >= 0.6:
        return "HIGH"
    elif abs_score >= 0.35:
        return "MEDIUM"
    elif abs_score >= 0.15:
        return "LOW"
    else:
        return "WEAK"


def _build_rationale(asset: Dict, signal: str, price_data: Dict) -> str:
    ticker = asset["ticker"]
    score = asset["sentiment_score"]
    n = asset["article_count"]
    sources = asset["source_count"]
    dist = asset.get("signal_distribution", {})

    pos = dist.get("STRONGLY_POSITIVE", 0) + dist.get("POSITIVE", 0)
    neg = dist.get("STRONGLY_NEGATIVE", 0) + dist.get("NEGATIVE", 0)

    parts = [
        f"Based on {n} articles from {sources} sources.",
        f"Sentiment score: {score:+.3f}.",
        f"Positive signals: {pos}, Negative signals: {neg}.",
    ]

    if price_data.get("change_pct") is not None:
        chg = price_data["change_pct"]
        direction = "up" if chg >= 0 else "down"
        parts.append(f"Price currently {direction} {abs(chg):.2f}% today.")

    parts.append(
        "⚠️ EDUCATIONAL SIMULATION ONLY — NOT FINANCIAL ADVICE."
    )

    return " ".join(parts)
