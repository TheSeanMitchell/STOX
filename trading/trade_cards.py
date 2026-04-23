"""
trading/trade_cards.py — Daily simulated trade card generator.
Picks top 10 BUY signals and allocates $100 each (simulated $1000 portfolio).
NOT real money. Educational simulation only.
"""

from datetime import datetime, timezone
from typing import Dict, List


ALLOCATION_PER_ASSET = 100.0  # Simulated dollars


def generate_trade_card(signals_data: Dict) -> Dict:
    """
    Generate today's simulated trade card from signals.
    Returns a trade card dict with asset entries and simulated prices.
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    top = signals_data.get("top_10", [])
    if not top:
        top = signals_data.get("all_signals", [])[:10]

    entries = []
    total_value = 0.0

    for asset in top[:10]:
        ticker = asset.get("ticker", "?")
        price = asset.get("price")
        signal = asset.get("signal", "HOLD")
        confidence = asset.get("confidence", 0.0)

        if price is None:
            shares = None
        else:
            shares = round(ALLOCATION_PER_ASSET / price, 6)

        entries.append({
            "ticker": ticker,
            "signal": signal,
            "confidence": confidence,
            "buy_price": price,
            "shares": shares,
            "allocated": ALLOCATION_PER_ASSET,
            "sentiment_score": asset.get("sentiment_score", 0.0),
            "rationale": asset.get("rationale", ""),
        })
        total_value += ALLOCATION_PER_ASSET

    return {
        "date": date_str,
        "generated_at": now.isoformat(),
        "assets": entries,
        "total_invested": total_value,
        "current_value": total_value,  # Will be updated by performance tracker
        "disclaimer": (
            "SIMULATED PORTFOLIO — Educational purposes only. "
            "Not real money, not financial advice."
        ),
    }
