"""
engine/sentiment.py — Multi-layer keyword + context sentiment scoring.
No external APIs required.
"""

import re
import math
import logging
from typing import Dict, List, Tuple

log = logging.getLogger("stox.sentiment")

# ─── KEYWORD LEXICON ────────────────────────────────────────────────────────

POSITIVE_KEYWORDS: List[Tuple[str, float]] = [
    # Earnings & Growth
    ("beat estimates", 1.8), ("beat expectations", 1.8), ("exceeded", 1.4),
    ("record revenue", 2.0), ("record profit", 2.0), ("record earnings", 2.0),
    ("profit surge", 1.8), ("revenue growth", 1.5), ("strong demand", 1.3),
    ("earnings beat", 1.8), ("guidance raised", 1.7), ("raised guidance", 1.7),
    ("raised forecast", 1.5), ("positive outlook", 1.2), ("upbeat outlook", 1.2),
    # Ratings & Analyst
    ("upgrade", 1.5), ("upgraded", 1.5), ("price target raised", 1.6),
    ("outperform", 1.4), ("buy rating", 1.5), ("strong buy", 1.8),
    ("overweight", 1.2), ("bullish", 1.3), ("bull case", 1.2),
    # Deals & Catalysts
    ("acquisition", 1.2), ("merger", 1.1), ("partnership", 1.0),
    ("deal signed", 1.3), ("contract won", 1.4), ("new contract", 1.2),
    ("breakthrough", 1.5), ("innovation", 0.8), ("expansion", 1.0),
    ("market share", 0.9), ("new product", 1.0), ("product launch", 1.1),
    # Macro positive
    ("rate cut", 1.2), ("stimulus", 1.0), ("economic growth", 1.0),
    ("jobs added", 0.8), ("consumer spending", 0.7),
    # AI / Tech tailwind
    ("artificial intelligence", 0.6), ("ai demand", 1.2), ("data center", 0.8),
    ("cloud growth", 1.0), ("semiconductor demand", 1.0),
]

NEGATIVE_KEYWORDS: List[Tuple[str, float]] = [
    # Earnings & Guidance misses
    ("missed estimates", -1.8), ("missed expectations", -1.8), ("below expectations", -1.6),
    ("earnings miss", -1.8), ("revenue decline", -1.5), ("guidance lowered", -1.7),
    ("lowered guidance", -1.7), ("guidance cut", -1.7), ("profit warning", -2.0),
    ("loss widened", -1.6), ("net loss", -1.2), ("operating loss", -1.3),
    # Legal & Regulatory
    ("lawsuit", -1.4), ("investigation", -1.5), ("fraud", -2.2),
    ("regulatory probe", -1.6), ("sec investigation", -2.0), ("doj probe", -1.8),
    ("class action", -1.6), ("recall", -1.5), ("safety concern", -1.2),
    ("data breach", -1.7), ("cybersecurity incident", -1.5),
    # Ratings & Analyst
    ("downgrade", -1.5), ("downgraded", -1.5), ("price target cut", -1.4),
    ("underperform", -1.3), ("sell rating", -1.5), ("bearish", -1.3),
    ("underweight", -1.1), ("short seller", -1.6),
    # Operational
    ("layoffs", -1.2), ("job cuts", -1.2), ("workforce reduction", -1.3),
    ("restructuring", -0.8), ("bankruptcy", -2.5), ("chapter 11", -2.5),
    ("debt default", -2.2), ("dilution", -1.3), ("stock dilution", -1.5),
    ("supply chain", -0.8), ("production halt", -1.5),
    # Macro negative
    ("rate hike", -0.9), ("inflation spike", -1.0), ("recession", -1.3),
    ("stagflation", -1.4), ("market crash", -1.8), ("volatility spike", -1.2),
    ("liquidity crisis", -1.8), ("bank run", -2.0),
]

# Compile for speed
_POS = [(re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE), w)
        for kw, w in POSITIVE_KEYWORDS]
_NEG = [(re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE), w)
        for kw, w in NEGATIVE_KEYWORDS]

# Negation patterns
NEGATION_RE = re.compile(
    r'\b(not|no|never|without|failed to|unable to|didn\'t|won\'t|cannot|can\'t)\b',
    re.IGNORECASE
)

NEGATION_WINDOW = 6  # words


def score_sentiment(item: Dict) -> Dict:
    """
    Score a normalized StoxItem for sentiment.
    Adds: sentiment_score, sentiment_label, matched_signals
    """
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    score, signals = _compute_score(text)

    # Apply weight
    weight = item.get("weight", 0.6)
    weighted_score = score * weight

    # Apply any hint from source (e.g. SEC filing type)
    hint = item.get("_sentiment_hint", 0.0)
    weighted_score += hint

    label = _score_to_label(weighted_score)

    result = dict(item)
    result.update({
        "sentiment_score": round(weighted_score, 3),
        "raw_sentiment": round(score, 3),
        "sentiment_label": label,
        "matched_signals": signals[:10],
    })
    return result


def _compute_score(text: str) -> Tuple[float, List[str]]:
    """Raw sentiment score and matched signals list."""
    words = text.split()
    signals = []
    total = 0.0

    for pattern, weight in _POS:
        matches = pattern.findall(text)
        for m in matches:
            if not _negated(text, words, m):
                total += weight
                signals.append(f"+{m}({weight:+.1f})")

    for pattern, weight in _NEG:
        matches = pattern.findall(text)
        for m in matches:
            if not _negated(text, words, m):
                total += weight  # weight is already negative
                signals.append(f"-{m}({weight:+.1f})")

    # Normalize via soft sigmoid
    score = _sigmoid_normalize(total)
    return score, signals


def _negated(text: str, words: List[str], match: str) -> bool:
    """Check if match is preceded by a negation word within a window."""
    match_pos = text.lower().find(match.lower())
    if match_pos == -1:
        return False
    pre_text = text[:match_pos]
    pre_words = pre_text.split()[-NEGATION_WINDOW:]
    return bool(NEGATION_RE.search(" ".join(pre_words)))


def _sigmoid_normalize(x: float) -> float:
    """Map raw score to [-1, 1] range via tanh."""
    return math.tanh(x / 5.0)


def _score_to_label(score: float) -> str:
    if score >= 0.5:
        return "STRONGLY_POSITIVE"
    elif score >= 0.2:
        return "POSITIVE"
    elif score <= -0.5:
        return "STRONGLY_NEGATIVE"
    elif score <= -0.2:
        return "NEGATIVE"
    else:
        return "NEUTRAL"
