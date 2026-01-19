"""
Script 10: Bank Comparison
Side-by-side comparison of major banks' silver exposure.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from pathlib import Path
from datetime import datetime
import requests

# Bank data
BANKS = [
    {'name': 'JPMorgan', 'ticker': 'JPM', 'position': 'LONG', 'oz': 750e6, 'exposure': '$437B', 'color': '#4ade80'},
    {'name': 'Morgan Stanley', 'ticker': 'MS', 'position': 'SHORT', 'oz': 300e6, 'exposure': '$18.5B', 'color': '#e31837'},
    {'name': 'Citigroup', 'ticker': 'C', 'position': 'SHORT', 'oz': 200e6, 'exposure': '$12.8B', 'color': '#e31837'},
    {'name': 'Bank of America', 'ticker': 'BAC', 'position': 'SHORT', 'oz': 150e6, 'exposure': '$8.2B', 'color': '#e31837'},
    {'name': 'Goldman Sachs', 'ticker': 'GS', 'position': 'SHORT', 'oz': 100e6, 'exposure': '$6.1B', 'color': '#ff8c42'},
]

def get_bank_prices():
    """Fetch current bank stock prices."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        prices = data['prices']
        return {
            'JPM': prices.get('jpmorgan', {}).get('change_pct', 0),
            'MS': prices.get('morgan_stanley', {}).get('change_pct', 0),
            'C': prices.get('citigroup', {}).get('change_pct', 0),
            'BAC': prices.get('bank_of_america', {}).get('change_pct', 0),
            'GS': prices.get('goldman', {}).get('change_pct', 0),
        }
    except:
        return {'JPM': 0, 'MS': -2, 'C': -4.5, 'BAC': -5.2, 'GS': -1}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size, bold=False):
    font_names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def format_oz(value):
    """Format ounces in millions."""
    return f"{value / 1e6:.0f}M oz"

def create_frame(t, duration, prices):
    """Create a single frame of bank comparison animation."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    brand_red = hex_to_rgb('#e31837')

    # Header
    font_header = get_font(60, bold=True)
    header = "BANK EXPOSURE"
    bbox = draw.textbbox((0, 0), header, font=font_header)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 150), header, fill=(255, 255, 255), font=font_header)

    # Subtitle
    font_sub = get_font(36)
    subtitle = "Silver Derivative Positions"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 230), subtitle, fill=(136, 136, 136), font=font_sub)

    # Bank cards
    card_start_y = 350
    card_height = 250
    card_spacing = 20
    card_margin = 50

    for i, bank in enumerate(BANKS):
        appear_time = i * 0.3
        if t < appear_time:
            continue

        alpha = min(1.0, (t - appear_time) / 0.3)
        y = card_start_y + i * (card_height + card_spacing)

        # Card background
        bg_alpha = int(30 * alpha)
        card_color = (bg_alpha, bg_alpha, bg_alpha)
        draw.rectangle([(card_margin, y), (width - card_margin, y + card_height)], fill=card_color, outline=(50, 50, 50))

        # Position indicator (left bar)
        bar_color = hex_to_rgb(bank['color'])
        bar_color = tuple(int(c * alpha) for c in bar_color)
        draw.rectangle([(card_margin, y), (card_margin + 8, y + card_height)], fill=bar_color)

        # Bank name
        font_name = get_font(48, bold=True)
        color = tuple(int(255 * alpha) for _ in range(3))
        draw.text((card_margin + 30, y + 20), bank['name'], fill=color, font=font_name)

        # Ticker
        font_ticker = get_font(28)
        ticker_color = tuple(int(136 * alpha) for _ in range(3))
        draw.text((card_margin + 30, y + 75), bank['ticker'], fill=ticker_color, font=font_ticker)

        # Position badge
        badge_color = hex_to_rgb(bank['color'])
        badge_color = tuple(int(c * alpha) for c in badge_color)
        font_badge = get_font(24, bold=True)
        badge_text = bank['position']
        badge_x = width - card_margin - 120
        draw.rectangle([(badge_x, y + 20), (badge_x + 100, y + 55)], fill=badge_color)
        draw.text((badge_x + 15, y + 25), badge_text, fill=(255, 255, 255), font=font_badge)

        # Stats row
        font_label = get_font(24)
        font_value = get_font(32, bold=True)

        # Position size
        draw.text((card_margin + 30, y + 130), "Position", fill=ticker_color, font=font_label)
        draw.text((card_margin + 30, y + 160), format_oz(bank['oz']), fill=color, font=font_value)

        # Exposure
        draw.text((card_margin + 250, y + 130), "Exposure", fill=ticker_color, font=font_label)
        draw.text((card_margin + 250, y + 160), bank['exposure'], fill=color, font=font_value)

        # Today's change
        change = prices.get(bank['ticker'], 0)
        change_color = hex_to_rgb('#4ade80') if change >= 0 else hex_to_rgb('#e31837')
        change_color = tuple(int(c * alpha) for c in change_color)

        draw.text((card_margin + 500, y + 130), "Today", fill=ticker_color, font=font_label)
        arrow = "▲" if change >= 0 else "▼"
        change_text = f"{arrow} {abs(change):.1f}%"
        draw.text((card_margin + 500, y + 160), change_text, fill=change_color, font=font_value)

    # Summary at bottom
    if t >= 2:
        alpha = min(1.0, (t - 2) / 1)

        summary_y = 1650
        font_summary = get_font(32, bold=True)

        # Total short
        total_short = sum(b['oz'] for b in BANKS if b['position'] == 'SHORT')
        short_color = tuple(int(c * alpha) for c in brand_red)
        draw.text((100, summary_y), f"Total Short: {format_oz(total_short)}", fill=short_color, font=font_summary)

        # JPM long
        jpm_long = BANKS[0]['oz']
        green = tuple(int(c * alpha) for c in hex_to_rgb('#4ade80'))
        draw.text((100, summary_y + 50), f"JPM Long: {format_oz(jpm_long)}", fill=green, font=font_summary)

        # Net exposure
        net = total_short - jpm_long
        net_color = short_color if net > 0 else green
        draw.text((600, summary_y + 25), f"Net Short: {format_oz(abs(net))}", fill=net_color, font=font_summary)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_bank_comparison():
    """Generate bank comparison video."""
    prices = get_bank_prices()

    duration = 10
    fps = 30

    print("Generating bank comparison video...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, prices)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"bank_comparison_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_bank_comparison()
