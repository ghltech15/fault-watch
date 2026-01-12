"""
Data Sources Configuration
URLs and API endpoints for various data sources
"""

SOURCES = {
    # SEC EDGAR
    'sec': {
        'base_url': 'https://www.sec.gov',
        'edgar_search': 'https://efts.sec.gov/LATEST/search-index',
        'company_search': 'https://www.sec.gov/cgi-bin/browse-edgar',
        'filings_rss': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&count=100&output=atom',
        'ciks': {
            'morgan_stanley': '895421',
            'citigroup': '831001',
            'jpmorgan': '19617',
            'goldman': '886982',
            'bank_of_america': '70858',
            'hsbc': '83246',
            'ubs': '1114446',
            'scotiabank': '1073251',
        },
    },

    # CFTC
    'cftc': {
        'cot_report': 'https://www.cftc.gov/dea/futures/other_lf.htm',
        'silver_disaggregated': 'https://www.cftc.gov/dea/futures/deacmxsf.htm',
        'enforcement': 'https://www.cftc.gov/LawRegulation/Enforcement/EnforcementActions/index.htm',
    },

    # Federal Reserve
    'fed': {
        'repo_ops': 'https://www.newyorkfed.org/markets/desk-operations/reverse-repo',
        'rrp_data': 'https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json',
        'h41_release': 'https://www.federalreserve.gov/releases/h41/',
        'fred_api': 'https://api.stlouisfed.org/fred/series/observations',
    },

    # COMEX/CME
    'comex': {
        'silver_inventory': 'https://www.cmegroup.com/delivery_reports/Silver_Stocks.xls',
        'gold_inventory': 'https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls',
        'delivery_notices': 'https://www.cmegroup.com/delivery_reports/',
        'open_interest': 'https://www.cmegroup.com/CmeWS/mvc/Volume/Product/SI',
    },

    # LBMA
    'lbma': {
        'silver_price': 'https://www.lbma.org.uk/prices-and-data/precious-metal-prices#/',
        'vault_data': 'https://www.lbma.org.uk/prices-and-data/london-vault-holdings-data',
    },

    # News Sources
    'news': {
        'kitco': 'https://www.kitco.com/news/rss/kitco-news-headlines.rss',
        'reuters_commodities': 'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best&best-sectors=commodities',
        'bloomberg_commodities': 'https://www.bloomberg.com/feeds/commodities.xml',
        'zerohedge': 'https://feeds.feedburner.com/zerohedge/feed',
        'seeking_alpha': 'https://seekingalpha.com/tag/silver.xml',
    },

    # Reddit
    'reddit': {
        'base_url': 'https://www.reddit.com',
        'api_base': 'https://oauth.reddit.com',
        'subreddits': ['wallstreetsilver', 'silverbugs', 'gold', 'wallstreetbets'],
    },

    # Physical Dealers (for premium monitoring)
    'dealers': {
        'apmex': 'https://www.apmex.com/silver',
        'jmbullion': 'https://www.jmbullion.com/silver/',
        'sdbullion': 'https://sdbullion.com/silver',
        'monument_metals': 'https://monumentmetals.com/silver.html',
        'bullion_exchanges': 'https://bullionexchanges.com/silver',
    },

    # Price APIs
    'prices': {
        'finnhub': 'https://finnhub.io/api/v1',
        'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart/',
        'kitco_spot': 'https://www.kitco.com/charts/livesilver.html',
    },

    # Twitter/X (via nitter or official API)
    'twitter': {
        'nitter_instances': [
            'https://nitter.net',
            'https://nitter.it',
            'https://nitter.nl',
        ],
    },
}

# Rate limiting configuration (requests per minute)
RATE_LIMITS = {
    'sec': 10,
    'fed': 30,
    'comex': 10,
    'finnhub': 60,
    'reddit': 60,
    'twitter': 30,
    'news': 30,
}

# Refresh intervals (seconds)
REFRESH_INTERVALS = {
    'prices': 60,           # 1 minute
    'alerts': 60,           # 1 minute
    'fed_repo': 3600,       # 1 hour
    'comex': 3600,          # 1 hour
    'sec_filings': 900,     # 15 minutes
    'news': 300,            # 5 minutes
    'social': 300,          # 5 minutes
    'dealers': 1800,        # 30 minutes
}
