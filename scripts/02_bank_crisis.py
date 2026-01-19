"""
Script 2: Bank Crisis Alert
Generates video when a major bank stock is crashing.
"""
import sys
sys.path.insert(0, '..')

import requests
from content_generator import ContentGenerator, TemplateType, VideoConfig

BANKS = {
    'morgan_stanley': {'name': 'Morgan Stanley', 'exposure': '$18.5B'},
    'citigroup': {'name': 'Citigroup', 'exposure': '$12.8B'},
    'bank_of_america': {'name': 'Bank of America', 'exposure': '$8.2B'},
    'jpmorgan': {'name': 'JPMorgan', 'exposure': '$437B (LONG)'},
    'goldman': {'name': 'Goldman Sachs', 'exposure': '$6.1B'},
}

def get_bank_data(bank_key='citigroup'):
    """Fetch bank price data from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        bank = data['prices'].get(bank_key, {})
        return bank.get('price', 100), bank.get('change_pct', -5.0)
    except:
        return 100, -5.0

def generate_bank_crisis(bank_key='citigroup'):
    """Generate bank crisis alert video."""
    price, change = get_bank_data(bank_key)
    bank_info = BANKS.get(bank_key, {'name': 'Unknown Bank', 'exposure': '$0'})

    gen = ContentGenerator()
    config = VideoConfig(duration=12, fps=30)

    data = {
        'bank': bank_info['name'],
        'price': price,
        'change': change,
        'exposure': bank_info['exposure'],
        'loss': f"${abs(change) * 0.5:.1f}B" if change < -5 else ''
    }

    path = gen.generate_video(data, TemplateType.BANK_CRISIS, config)
    print(f"Generated: {path}")
    return path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bank', default='citigroup', choices=list(BANKS.keys()))
    args = parser.parse_args()
    generate_bank_crisis(args.bank)
