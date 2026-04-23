"""
trading/performance.py — Track historical trade card performance.
The FOMO Engine: "Had you invested on [date], you'd have [X] today."
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

log = logging.getLogger("stox.performance")

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False


def update_performance(all_cards: List[Dict]) -> Dict:
    """
    Update all historical trade cards with current prices.
    Returns a performance summary.
    """
    now = datetime.now(timezone.utc).isoformat()
    updated_cards = []
    all_time_best = None
    all_time_worst = None

    for card in all_cards:
        updated = _refresh_card(card)
        updated_cards.append(updated)

        pct = updated.get("percent_return", 0)
        if all_time_best is None or pct > all_time_best["percent_return"]:
            all_time_best = updated
        if all_time_worst is None or pct < all_time_worst["percent_return"]:
            all_time_worst = updated

    # FOMO metric: best-ever card
    fomo_message = None
    if all_time_best:
        d = all_time_best["date"]
        iv = all_time_best.get("total_invested", 1000)
        cv = all_time_best.get("current_value", iv)
        pct = all_time_best.get("percent_return", 0)
        fomo_message = (
            f"Had you followed our simulated picks on {d}, "
            f"your $1,000 would now be worth ${cv:,.2f} "
            f"({pct:+.1f}%). 🚀"
        )

    return {
        "updated_at": now,
        "total_cards": len(updated_cards),
        "cards": updated_cards,
        "all_time_best": all_time_best,
        "all_time_worst": all_time_worst,
        "fomo_message": fomo_message,
    }


def _refresh_card(card: Dict) -> Dict:
    card = dict(card)
    total_invested = card.get("total_invested", 0)
    if total_invested <= 0:
        return card

    current_value = 0.0
    assets = card.get("assets", [])
    updated_assets = []

    for entry in assets:
        ticker = entry.get("ticker", "")
        buy_price = entry.get("buy_price")
        shares = entry.get("shares")
        allocated = entry.get("allocated", 100.0)

        current_price = _fetch_current_price(ticker)

        if buy_price and shares and current_price:
            position_value = shares * current_price
        else:
            position_value = allocated  # No data = assume flat

        pct = ((position_value - allocated) / allocated * 100) if allocated else 0

        updated_entry = dict(entry)
        updated_entry.update({
            "current_price": current_price,
            "current_value": round(position_value, 2),
            "return_pct": round(pct, 2),
        })
        updated_assets.append(updated_entry)
        current_value += position_value

    pct_return = ((current_value - total_invested) / total_invested * 100) if total_invested else 0

    card["assets"] = updated_assets
    card["current_value"] = round(current_value, 2)
    card["percent_return"] = round(pct_return, 2)
    card["last_updated"] = datetime.now(timezone.utc).isoformat()
    return card


def _fetch_current_price(ticker: str) -> float | None:
    if not YF_AVAILABLE:
        return None
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None
