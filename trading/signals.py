"""
trading/signals.py — Build the final signals output payload.
"""

from datetime import datetime, timezone
from typing import Dict, List


def build_signals(predictions: List[Dict]) -> Dict:
    """
    Organize predictions into a structured signals payload.
    """
    now = datetime.now(timezone.utc).isoformat()

    by_signal = {
        "STRONG_BUY": [],
        "BUY": [],
        "HOLD": [],
        "SELL": [],
        "STRONG_SELL": [],
    }

    for p in predictions:
        sig = p.get("signal", "HOLD")
        by_signal.setdefault(sig, []).append(p)

    top_10 = [
        p for p in predictions
        if p["signal"] in ("STRONG_BUY", "BUY")
    ][:10]

    return {
        "generated_at": now,
        "disclaimer": (
            "PROJECT STOX is an educational simulation. "
            "All signals are simulated and do NOT constitute financial advice. "
            "Past simulated performance does not guarantee future results."
        ),
        "summary": {
            "total_tracked": len(predictions),
            "strong_buy_count": len(by_signal["STRONG_BUY"]),
            "buy_count": len(by_signal["BUY"]),
            "hold_count": len(by_signal["HOLD"]),
            "sell_count": len(by_signal["SELL"]),
            "strong_sell_count": len(by_signal["STRONG_SELL"]),
        },
        "top_10": top_10,
        "all_signals": predictions,
        "by_signal": by_signal,
    }
