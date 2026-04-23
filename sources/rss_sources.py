"""
sources/rss_sources.py — Curated list of high-trust financial RSS feeds.
Tier 1 = highest trust. Tier 2 = good. Tier 3 = supplemental.
"""

RSS_SOURCES = [
    # ─── TIER 1: Major Financial News ───────────────────────────────────
    {
        "label": "Reuters Markets",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "Reuters Finance",
        "url": "https://feeds.reuters.com/reuters/financialsNews",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "CNBC Markets",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "CNBC Finance",
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "MarketWatch Top Stories",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "MarketWatch Economy",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_economy",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rss",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "Investing.com News",
        "url": "https://www.investing.com/rss/news.rss",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "Seeking Alpha Market Currents",
        "url": "https://seekingalpha.com/market_currents.xml",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "Financial Times",
        "url": "https://www.ft.com/rss/home/uk",
        "type": "rss",
        "tier": 1,
    },

    # ─── TIER 1: IPO & Filings ───────────────────────────────────────────
    {
        "label": "SEC EDGAR Latest Filings",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=S-1&dateb=&owner=include&count=20&search_text=&output=atom",
        "type": "rss",
        "tier": 1,
    },
    {
        "label": "SEC EDGAR 8-K Filings",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&dateb=&owner=include&count=20&search_text=&output=atom",
        "type": "rss",
        "tier": 1,
    },

    # ─── TIER 2: Commodities & Macro ────────────────────────────────────
    {
        "label": "Kitco Gold",
        "url": "https://www.kitco.com/rss/news/kitcoNews.rss",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "OilPrice",
        "url": "https://oilprice.com/rss/main",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "CoinTelegraph",
        "url": "https://cointelegraph.com/rss",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "Benzinga",
        "url": "https://www.benzinga.com/feed",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "The Motley Fool",
        "url": "https://www.fool.com/feeds/syndication/rss",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "Barrons Markets",
        "url": "https://www.barrons.com/feed/rss/markets",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "Investopedia",
        "url": "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "Bloomberg Markets",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
        "type": "rss",
        "tier": 2,
    },
    {
        "label": "The Street",
        "url": "https://www.thestreet.com/rss/00000000-0000-0000-0000-000000000000.rss",
        "type": "rss",
        "tier": 2,
    },

    # ─── TIER 3: Social / Broader Signal ────────────────────────────────
    {
        "label": "Reddit r/stocks",
        "url": "https://www.reddit.com/r/stocks/.rss",
        "type": "rss",
        "tier": 3,
    },
    {
        "label": "Reddit r/investing",
        "url": "https://www.reddit.com/r/investing/.rss",
        "type": "rss",
        "tier": 3,
    },
    {
        "label": "Reddit r/wallstreetbets",
        "url": "https://www.reddit.com/r/wallstreetbets/.rss",
        "type": "rss",
        "tier": 3,
    },
    {
        "label": "Reddit r/cryptocurrency",
        "url": "https://www.reddit.com/r/cryptocurrency/.rss",
        "type": "rss",
        "tier": 3,
    },
    {
        "label": "Hacker News Finance",
        "url": "https://hnrss.org/newest?q=stocks+finance+market",
        "type": "rss",
        "tier": 3,
    },
]
