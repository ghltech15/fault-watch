"""
Script 1: Silver Breakout Alert
Generates dramatic video when silver breaks key price levels.
"""
import sys
sys.path.insert(0, '..')

import requests
from content_generator import ContentGenerator, TemplateType, VideoConfig

def get_silver_price():
    """Fetch current silver price from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        silver = data['prices'].get('silver', {})
        return silver.get('price', 91.57), silver.get('change_pct', 5.0)
    except:
        return 91.57, 5.0  # Fallback

def generate_silver_breakout():
    """Generate silver breakout alert video."""
    price, change = get_silver_price()

    gen = ContentGenerator()
    config = VideoConfig(duration=10, fps=30)

    data = {
        'asset': 'SILVER',
        'price': price,
        'change': change
    }

    path = gen.generate_video(data, TemplateType.PRICE_ALERT, config)
    print(f"Generated: {path}")
    return path

if __name__ == "__main__":
    generate_silver_breakout()
