"""
Keywords Configuration
Search terms for monitoring various data sources
"""

KEYWORDS = {
    # Bank-specific keywords
    'banks': {
        'morgan_stanley': [
            'morgan stanley', 'MS stock', '$MS', 'morgan stanley silver',
            'morgan stanley short', 'morgan stanley SEC', 'MS derivatives',
        ],
        'citigroup': [
            'citigroup', 'citi bank', '$C', 'citigroup silver',
            'citigroup short', 'citi derivatives', "lloyd's citigroup",
        ],
        'hsbc': [
            'HSBC', '$HSBC', 'HSBC silver', 'HSBC short',
            'HSBC precious metals', 'HSBC London',
        ],
        'ubs': [
            'UBS', '$UBS', 'UBS silver', 'UBS nationalization',
            'UBS Swiss', 'UBS short', 'Swiss National Bank UBS',
        ],
        'jpmorgan': [
            'jpmorgan', 'jp morgan', 'jamie dimon', '$JPM',
            'jpmorgan silver', 'jpmorgan gold', 'jpmorgan vault',
        ],
        'scotiabank': [
            'scotiabank', 'scotia mocatta', '$BNS', 'scotiabank silver',
            'scotiabank precious metals',
        ],
    },

    # Silver/Gold keywords
    'precious_metals': [
        'silver', 'gold', 'precious metals', 'bullion',
        'silver squeeze', 'silver short', 'comex silver',
        'LBMA silver', 'silver delivery', 'silver vault',
        'physical silver', 'paper silver', 'silver manipulation',
        'SLV', 'PSLV', 'silver ETF', 'silver price',
    ],

    # Regulatory keywords
    'regulatory': [
        'SEC', 'CFTC', 'OCC', 'Fed', 'Federal Reserve',
        'wells notice', 'enforcement action', 'investigation',
        'subpoena', 'settlement', 'fine', 'penalty',
        'market manipulation', 'spoofing', 'naked short',
        'position limits', 'margin call', 'margin requirement',
    ],

    # Crisis indicators
    'crisis': [
        'bank run', 'liquidity crisis', 'insolvency', 'bankruptcy',
        'default', 'credit event', 'systemic risk', 'contagion',
        'bailout', 'bail-in', 'nationalization', 'FDIC',
        'deposit flight', 'bank failure', 'stress test',
    ],

    # COMEX/Exchange keywords
    'exchange': [
        'COMEX', 'LBMA', 'delivery', 'settlement', 'standing for delivery',
        'registered', 'eligible', 'vault inventory', 'warehouse',
        'open interest', 'futures', 'options', 'expiration',
        'first notice day', 'delivery month', 'rollover',
    ],

    # Fed/Monetary keywords
    'fed': [
        'fed repo', 'reverse repo', 'RRP', 'overnight repo',
        'fed balance sheet', 'QE', 'QT', 'interest rate',
        'fed funds', 'discount window', 'emergency lending',
        'fed intervention', 'liquidity injection',
    ],

    # Insurance/Lloyd's keywords
    'insurance': [
        "lloyd's", "lloyd's of london", 'insurance coverage',
        'derivatives insurance', 'counterparty risk',
        'credit default swap', 'CDS', 'reinsurance',
    ],

    # Key people to monitor
    'people': [
        'jamie dimon', 'james gorman', 'jane fraser',
        'jerome powell', 'gary gensler', 'rostin behnam',
    ],

    # Subreddits to monitor
    'subreddits': [
        'wallstreetsilver', 'silverbugs', 'gold', 'preciousmetals',
        'wallstreetbets', 'stocks', 'investing', 'economics',
    ],

    # Twitter accounts to monitor
    'twitter_accounts': [
        'federalreserve', 'SEC_News', 'ABOREIS',
        'Sprott', 'KitcoNews', 'Reuters', 'Bloomberg',
        'zerohedge', 'TFMetals', 'GoldTelegraph',
        'WallStreetSilv', 'SilverSqueeze',
    ],
}

# High-priority keywords that trigger immediate alerts
CRITICAL_KEYWORDS = [
    'wells notice', 'enforcement action', 'investigation',
    'bank run', 'insolvency', 'bankruptcy', 'default',
    'nationalization', 'bailout', 'emergency',
    'delivery failure', 'force majeure', 'trading halt',
    'margin call', 'liquidation',
]

# Keywords that indicate positive silver thesis
BULLISH_KEYWORDS = [
    'silver squeeze', 'delivery demand', 'vault drain',
    'physical shortage', 'premium spike', 'supply crisis',
    'industrial demand', 'solar demand', 'EV demand',
]

# Keywords that indicate negative/risk
BEARISH_KEYWORDS = [
    'paper dump', 'naked short', 'manipulation',
    'smash', 'takedown', 'raid', 'waterfall',
]
