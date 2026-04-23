# 🚀 PROJECT STOX

**A fully automated, zero-cost financial intelligence engine.**

> ⚠️ **EDUCATIONAL SIMULATION ONLY. NOT FINANCIAL ADVICE.**

---

## What Is This?

PROJECT STOX is an information refinery — it aggregates global financial news, runs it through a sentiment engine, generates simulated trade signals, and tracks hypothetical portfolio performance over time.

**Zero cost. Zero paid APIs. Fully automated.**

---

## Architecture

```
bot.py                   ← Orchestrator
├── core/
│   ├── fetcher.py       ← Parallel RSS/JSON fetching
│   ├── normalizer.py    ← Unified StoxItem schema
│   ├── deduplicator.py  ← Exact + fuzzy dedup
│   └── cache.py         ← Disk-backed TTL cache
├── sources/
│   ├── rss_sources.py   ← 25+ curated financial RSS feeds
│   ├── yfinance_source.py ← Free market data
│   ├── google_news.py   ← Dynamic query generator
│   └── sec_edgar.py     ← SEC filings (S-1, 8-K, 10-K)
├── engine/
│   ├── sentiment.py     ← Keyword sentiment with negation
│   ├── scorer.py        ← Recency-weighted asset aggregation
│   └── predictor.py     ← Rule-based BUY/SELL/HOLD signals
├── trading/
│   ├── signals.py       ← Signal payload builder
│   ├── trade_cards.py   ← Daily $1,000 simulated portfolio
│   └── performance.py   ← Historical tracking + FOMO engine
├── output/
│   ├── json_builder.py  ← Canonical JSON output
│   └── site_generator.py ← GitHub Pages data export
├── .github/workflows/
│   ├── hourly.yml       ← Signal refresh every hour
│   └── daily.yml        ← Trade cards + performance daily
└── docs/
    └── index.html       ← Bloomberg-style dashboard
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/stox
cd stox
pip install -r requirements.txt

# Full run (hourly + daily)
python bot.py --mode full

# Hourly signals only
python bot.py --mode hourly

# Daily trade card + performance
python bot.py --mode daily
```

---

## Deployment (GitHub Actions)

1. Fork / push this repo to GitHub
2. Enable GitHub Actions (Settings → Actions → Allow)
3. Enable GitHub Pages from `docs/` folder
4. The workflows will auto-run:
   - **Every hour**: fetch → normalize → score → signals
   - **Daily at 5:30 PM EST**: trade card + performance update

No secrets or API keys required for the base system.

---

## Data Sources

| Source | Tier | Type |
|--------|------|------|
| Reuters | 1 | RSS |
| CNBC | 1 | RSS |
| MarketWatch | 1 | RSS |
| Yahoo Finance | 1 | RSS |
| SEC EDGAR | 1 | RSS/Atom |
| Investing.com | 1 | RSS |
| Bloomberg | 2 | RSS |
| CoinDesk | 2 | RSS |
| Reddit (r/stocks, r/investing, r/WSB) | 3 | RSS |
| Google News (dynamic queries) | 2 | RSS |
| yfinance | — | API (free) |

---

## Signal Logic

```
IF weighted_sentiment_score > +0.45 → STRONG_BUY
IF weighted_sentiment_score > +0.20 → BUY
IF weighted_sentiment_score < -0.45 → STRONG_SELL
IF weighted_sentiment_score < -0.20 → SELL
ELSE                                 → HOLD
```

Confidence is computed from:
- Article volume
- Source diversity  
- Tier diversity

---

## Trade Card Simulation

Each day, the top 10 BUY signals receive a simulated $100 allocation each ($1,000 total portfolio). Performance is tracked using live prices from yfinance.

**The FOMO Engine** shows: _"Had you followed the simulated picks on [date], you'd have $X today."_

---

## Frontend

The `docs/` folder is a static GitHub Pages site with:
- Live signal dashboard
- Trade card history
- FOMO performance tracker
- Full article intelligence feed
- 3 local user profiles (localStorage)

---

## Disclaimer

PROJECT STOX is an **educational simulation**. All signals, portfolios, and performance metrics are **simulated and hypothetical**. Nothing in this system constitutes financial advice. Always consult a licensed financial professional before making investment decisions.

---

*Built for learning. Powered by open data. Zero cost.*
