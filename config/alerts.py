"""
Alert Thresholds Configuration
Defines when alerts should be triggered
"""

ALERT_THRESHOLDS = {
    # Price alerts
    'prices': {
        'silver': {
            'spike_pct': 5,          # 5% daily spike
            'crash_pct': -5,         # 5% daily crash
            'breakout_price': 50,    # Above $50 = major breakout
            'crisis_price': 80,      # Above $80 = bank insolvency territory
            'critical_price': 100,   # Above $100 = systemic crisis
        },
        'gold': {
            'spike_pct': 3,
            'crash_pct': -3,
            'breakout_price': 3000,
            'crisis_price': 4000,
        },
        'vix': {
            'elevated': 25,
            'high': 30,
            'panic': 40,
        },
    },

    # Bank stock alerts
    'bank_stocks': {
        'daily_drop_warning': -3,     # 3% daily drop
        'daily_drop_critical': -7,    # 7% daily drop
        'weekly_drop_warning': -10,   # 10% weekly drop
        'weekly_drop_critical': -20,  # 20% weekly drop
        'price_levels': {
            'MS': {'warning': 100, 'critical': 80},
            'C': {'warning': 60, 'critical': 45},
            'HSBC': {'warning': 40, 'critical': 30},
            'BNS': {'warning': 50, 'critical': 35},
        },
    },

    # Fed repo alerts
    'fed_repo': {
        'daily_warning': 20,          # $20B daily repo
        'daily_critical': 50,         # $50B daily repo
        'weekly_warning': 100,        # $100B weekly
        'weekly_critical': 250,       # $250B weekly
    },

    # COMEX inventory alerts
    'comex': {
        'registered_drop_pct': -10,   # 10% drop in registered
        'coverage_ratio_warning': 2,  # 2:1 paper to physical
        'coverage_ratio_critical': 3, # 3:1 paper to physical
        'days_supply_warning': 30,    # 30 days of supply
        'days_supply_critical': 14,   # 14 days of supply
    },

    # Physical premium alerts
    'premiums': {
        'spot_premium_warning': 15,   # 15% over spot
        'spot_premium_critical': 25,  # 25% over spot
        'dealer_shortage': True,      # Out of stock alerts
    },

    # Social media alerts
    'social': {
        'viral_threshold': 1000,      # Likes/upvotes for viral
        'mention_spike_pct': 200,     # 200% increase in mentions
        'sentiment_shift': 0.3,       # 30% sentiment shift
    },

    # Countdown alerts
    'deadlines': {
        'critical_days': 3,           # 3 days or less
        'warning_days': 7,            # 7 days or less
        'approaching_days': 14,       # 14 days or less
    },

    # Credit stress alerts
    'credit': {
        'ted_spread_warning': 0.5,    # 50 basis points
        'ted_spread_critical': 1.0,   # 100 basis points
        'high_yield_spread_warning': 500,   # 500 bp
        'high_yield_spread_critical': 800,  # 800 bp
    },
}

# Alert priority mapping
ALERT_PRIORITY = {
    'nationalization': 1,
    'bank_failure': 1,
    'trading_halt': 1,
    'delivery_failure': 1,
    'wells_notice': 2,
    'enforcement_action': 2,
    'bank_stock_crash': 2,
    'silver_breakout': 3,
    'fed_repo_spike': 3,
    'comex_drain': 3,
    'deadline_imminent': 4,
    'price_alert': 5,
    'news_alert': 6,
    'social_alert': 7,
}

# Notification channels
NOTIFICATION_CHANNELS = {
    'critical': ['email', 'slack', 'push'],
    'high': ['email', 'slack'],
    'medium': ['slack'],
    'low': ['dashboard_only'],
}
