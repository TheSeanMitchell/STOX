"""
sources/yfinance_source.py — Pull live market data (prices, volume, ratios)
via yfinance (free, no API key required).
"""

import logging
from typing import Dict, List, Optional

log = logging.getLogger("stox.yfinance")

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    log.warning("yfinance not installed. Market data will be unavailable.")


# Baseline watchlist — always fetched regardless of signal mentions
BASE_WATCHLIST = [
    # Mega cap tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    # Finance
    "JPM", "BAC", "GS", "V", "MA",
    # ETFs (market proxies)
    "SPY", "QQQ", "IWM", "DIA",
    # Commodities ETFs
    "GLD", "SLV", "USO",
    # Crypto (via yfinance)
    "BTC-USD", "ETH-USD", "SOL-USD",
]


def fetch_market_data(tickers: List[str] = None) -> Dict[str, Dict]:
    """
    Fetch current market data for given tickers + base watchlist.
    Returns { ticker: { price, change_pct, volume, market_cap, pe_ratio, ... } }
    """
    if not YF_AVAILABLE:
        return _mock_market_data(tickers or BASE_WATCHLIST)

    all_tickers = list(set((tickers or []) + BASE_WATCHLIST))
    # Normalize crypto tickers
    all_tickers = [_normalize_ticker(t) for t in all_tickers]
    all_tickers = list(set(filter(None, all_tickers)))

    results = {}
    try:
        # Batch download for efficiency
        data = yf.download(
            tickers=all_tickers,
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )

        for ticker in all_tickers:
            try:
                results[ticker] = _extract_ticker_data(ticker, data)
            except Exception as e:
                log.debug(f"No data for {ticker}: {e}")
                results[ticker] = _empty_ticker(ticker)

        # Fetch additional metadata (slower — only for top tickers)
        _enrich_with_info(results, all_tickers[:20])

    except Exception as e:
        log.warning(f"yfinance batch download failed: {e}")
        return _mock_market_data(all_tickers)

    return results


def _extract_ticker_data(ticker: str, data) -> Dict:
    try:
        if len(data.columns.levels[0]) > 1:
            # Multi-ticker download
            close = data["Close"][ticker].dropna()
        else:
            close = data["Close"].dropna()

        if len(close) < 1:
            return _empty_ticker(ticker)

        latest = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else latest
        change_pct = ((latest - prev) / prev * 100) if prev else 0.0

        return {
            "ticker": ticker,
            "price": round(latest, 4),
            "prev_close": round(prev, 4),
            "change_pct": round(change_pct, 2),
            "volume": None,
            "market_cap": None,
            "pe_ratio": None,
            "52w_high": None,
            "52w_low": None,
        }
    except Exception:
        return _empty_ticker(ticker)


def _enrich_with_info(results: Dict, tickers: List[str]):
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).fast_info
            if ticker in results:
                results[ticker].update({
                    "market_cap": getattr(info, "market_cap", None),
                    "52w_high": getattr(info, "year_high", None),
                    "52w_low": getattr(info, "year_low", None),
                })
        except Exception:
            pass


def _normalize_ticker(ticker: str) -> str:
    # Map raw crypto symbols to yfinance format
    crypto_map = {
        "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD",
        "ADA": "ADA-USD", "DOGE": "DOGE-USD", "XRP": "XRP-USD",
        "BNB": "BNB-USD", "AVAX": "AVAX-USD",
    }
    return crypto_map.get(ticker, ticker)


def _empty_ticker(ticker: str) -> Dict:
    return {
        "ticker": ticker,
        "price": None,
        "prev_close": None,
        "change_pct": None,
        "volume": None,
        "market_cap": None,
        "pe_ratio": None,
        "52w_high": None,
        "52w_low": None,
    }


def _mock_market_data(tickers: List[str]) -> Dict:
    """Return placeholder data when yfinance is unavailable."""
    import random
    results = {}
    for ticker in tickers:
        base = random.uniform(50, 500)
        chg = random.uniform(-3, 3)
        results[ticker] = {
            "ticker": ticker,
            "price": round(base, 2),
            "prev_close": round(base * (1 - chg / 100), 2),
            "change_pct": round(chg, 2),
            "volume": random.randint(1_000_000, 50_000_000),
            "market_cap": None,
            "pe_ratio": None,
            "52w_high": round(base * 1.3, 2),
            "52w_low": round(base * 0.7, 2),
            "_mock": True,
        }
    return results
