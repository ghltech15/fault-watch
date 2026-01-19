"""
Script 3: Countdown Deadline
Generates dramatic countdown video for key deadlines.
"""
import sys
sys.path.insert(0, '..')

import requests
from datetime import datetime
from content_generator import ContentGenerator, TemplateType, VideoConfig

DEADLINES = {
    'sec': {
        'name': 'SEC Filing Deadline',
        'date': '2026-02-15',
        'description': 'SEC requires position disclosure'
    },
    'lloyds': {
        'name': "Lloyd's Insurance Deadline",
        'date': '2026-01-31',
        'description': 'Bullion bank insurance deadline'
    },
    'comex': {
        'name': 'COMEX Delivery',
        'date': '2026-03-27',
        'description': 'March silver futures delivery'
    },
    'basel3': {
        'name': 'Basel III Compliance',
        'date': '2026-06-30',
        'description': 'Gold/Silver NSFR requirements'
    }
}

def calculate_days(deadline_date):
    """Calculate days until deadline."""
    deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
    today = datetime.now()
    delta = deadline - today
    return max(0, delta.days)

def generate_countdown(deadline_key='lloyds'):
    """Generate countdown video for deadline."""
    deadline = DEADLINES.get(deadline_key, DEADLINES['lloyds'])
    days = calculate_days(deadline['date'])

    gen = ContentGenerator()
    config = VideoConfig(duration=10, fps=30)

    # Format the date nicely
    deadline_dt = datetime.strptime(deadline['date'], '%Y-%m-%d')
    formatted_date = deadline_dt.strftime('%B %d, %Y')

    data = {
        'days': days,
        'event': deadline['name'],
        'date': formatted_date
    }

    path = gen.generate_video(data, TemplateType.COUNTDOWN, config)
    print(f"Generated: {path}")
    print(f"  {days} days until {deadline['name']}")
    return path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--deadline', default='lloyds', choices=list(DEADLINES.keys()))
    args = parser.parse_args()
    generate_countdown(args.deadline)
