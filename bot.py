#!/usr/bin/env python3
"""
PROJECT STOX — Orchestrator
Educational financial intelligence simulation engine.
NOT financial advice. Simulated data only.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone

# --- Module imports ---
from core.fetcher import fetch_all_sources
from core.normalizer import normalize_items
from core.deduplicator import deduplicate
from core.cache import Cache

from sources.rss_sources import RSS_SOURCES
from sources.yfinance_source import fetch_market_data
from sources.google_news import build_google_news_queries
from sources.sec_edgar import fetch_edgar_filings

from engine.sentiment import score_sentiment
from engine.scorer import aggregate_scores
from engine.predictor import generate_predictions

from trading.signals import build_signals
from trading.trade_cards import generate_trade_card
from trading.performance import update_performance

from output.json_builder import build_output_json
from output.site_generator import generate_site

# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("stox")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def run_hourly():
    """Fetch → normalize → score → predict → write JSON."""
    log.info("=== STOX HOURLY JOB STARTED ===")
    cache = Cache(DATA_DIR)

    # 1. Fetch
    log.info("Fetching RSS sources...")
    raw_rss = fetch_all_sources(RSS_SOURCES, cache)

    log.info("Fetching Google News queries...")
    gn_queries = build_google_news_queries()
    raw_gn = fetch_all_sources(gn_queries, cache)

    log.info("Fetching SEC EDGAR filings...")
    raw_edgar = fetch_edgar_filings(cache)

    raw_items = raw_rss + raw_gn + raw_edgar
    log.info(f"Total raw items: {len(raw_items)}")

    # 2. Normalize
    normalized = normalize_items(raw_items)
    log.info(f"Normalized: {len(normalized)} items")

    # 3. Deduplicate
    unique = deduplicate(normalized, cache)
    log.info(f"After dedup: {len(unique)} unique items")

    # 4. Sentiment scoring
    scored = [score_sentiment(item) for item in unique]

    # 5. Aggregate per asset
    aggregated = aggregate_scores(scored)

    # 6. Market data (prices)
    tickers = list(aggregated.keys())[:50]
    market_data = fetch_market_data(tickers)

    # 7. Predictions
    predictions = generate_predictions(aggregated, market_data)

    # 8. Signals
    signals = build_signals(predictions)

    # 9. Output JSON
    output = build_output_json(
        signals=signals,
        aggregated=aggregated,
        market_data=market_data,
        items=scored,
        run_type="hourly"
    )
    _write_json(output, "signals.json")
    _write_json(scored[:200], "articles.json")

    log.info("=== HOURLY JOB COMPLETE ===")


def run_daily():
    """Generate trade card + update performance tracker."""
    log.info("=== STOX DAILY JOB STARTED ===")
    cache = Cache(DATA_DIR)

    # Load latest signals
    signals_path = os.path.join(DATA_DIR, "signals.json")
    if not os.path.exists(signals_path):
        log.warning("No signals.json found — run hourly job first.")
        return

    with open(signals_path) as f:
        signals_data = json.load(f)

    # Generate today's trade card
    trade_card = generate_trade_card(signals_data)
    _append_json(trade_card, "trade_cards.json")

    # Update historical performance
    cards_path = os.path.join(DATA_DIR, "trade_cards.json")
    with open(cards_path) as f:
        all_cards = json.load(f)

    performance = update_performance(all_cards)
    _write_json(performance, "performance.json")

    # Regenerate site
    generate_site(DATA_DIR, "docs")

    log.info("=== DAILY JOB COMPLETE ===")


def run_full():
    """Run hourly then daily (local dev / first-time setup)."""
    run_hourly()
    run_daily()


def _write_json(data, filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log.info(f"Wrote {path}")


def _append_json(item, filename):
    path = os.path.join(DATA_DIR, filename)
    existing = []
    if os.path.exists(path):
        with open(path) as f:
            existing = json.load(f)
    existing.append(item)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2, default=str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PROJECT STOX Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["hourly", "daily", "full"],
        default="full",
        help="Run mode"
    )
    args = parser.parse_args()

    if args.mode == "hourly":
        run_hourly()
    elif args.mode == "daily":
        run_daily()
    else:
        run_full()
