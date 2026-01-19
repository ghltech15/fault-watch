"""
Script 4: Daily Summary
Generates daily market recap video with all key metrics.
"""
import sys
sys.path.insert(0, '..')

import requests
from datetime import datetime
from content_generator import ContentGenerator, TemplateType, VideoConfig

def get_dashboard_data():
    """Fetch all dashboard data from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        prices = data['prices']
        return {
            'silver': prices.get('silver', {}).get('price', 0),
            'gold': prices.get('gold', {}).get('price', 0),
            'ms': prices.get('morgan_stanley', {}).get('price', 0),
            'vix': prices.get('vix_futures', {}).get('price', 0),
            'risk': data.get('risk_index', 0)
        }
    except Exception as e:
        print(f"API error: {e}")
        return {'silver': 91.57, 'gold': 4243, 'ms': 180, 'vix': 27, 'risk': 5.0}

def generate_daily_summary():
    """Generate daily summary video."""
    data = get_dashboard_data()
    data['date'] = datetime.now().strftime('%B %d, %Y')

    gen = ContentGenerator()
    config = VideoConfig(duration=15, fps=30)

    path = gen.generate_video(data, TemplateType.DAILY_SUMMARY, config)
    print(f"Generated: {path}")
    print(f"  Silver: ${data['silver']:.2f}")
    print(f"  Gold: ${data['gold']:.2f}")
    print(f"  Risk Index: {data['risk']:.1f}")
    return path

if __name__ == "__main__":
    generate_daily_summary()
