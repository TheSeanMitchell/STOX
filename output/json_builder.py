"""
output/json_builder.py — Build the canonical output JSON payload.
"""

from datetime import datetime, timezone
from typing import Dict, List


VERSION = "1.0.0"


def build_output_json(
    signals: Dict,
    aggregated: Dict,
    market_data: Dict,
    items: List[Dict],
    run_type: str = "hourly",
) -> Dict:
    """
    Build the master signals.json payload.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Top movers by price change
    top_movers = _top_movers(market_data, n=10)

    return {
        "meta": {
            "version": VERSION,
            "project": "STOX",
            "run_type": run_type,
            "generated_at": now,
            "disclaimer": (
                "PROJECT STOX is an educational simulation. "
                "All content is for informational and entertainment purposes only. "
                "NOT financial advice. Always consult a licensed professional."
            ),
        },
        "summary": signals.get("summary", {}),
        "top_10": signals.get("top_10", []),
        "all_signals": signals.get("all_signals", []),
        "by_signal": signals.get("by_signal", {}),
        "market_snapshot": {
            "top_movers": top_movers,
            "tickers": {
                k: {
                    "price": v.get("price"),
                    "change_pct": v.get("change_pct"),
                }
                for k, v in list(market_data.items())[:30]
            },
        },
        "article_count": len(items),
        "asset_count": len(aggregated),
    }


def _top_movers(market_data: Dict, n: int = 10) -> List[Dict]:
    movers = []
    for ticker, data in market_data.items():
        chg = data.get("change_pct")
        price = data.get("price")
        if chg is not None and price is not None:
            movers.append({
                "ticker": ticker,
                "price": price,
                "change_pct": chg,
            })
    movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return movers[:n]
