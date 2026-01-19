"""
Script 9: Breaking News Alert
CNN-style breaking news banner with scrolling ticker.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from pathlib import Path
from datetime import datetime
import requests

def get_latest_alert():
    """Fetch latest alert from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        alerts = data.get('alerts', [])
        if alerts:
            return alerts[0]
        return None
    except:
        return None

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

def create_frame(t, duration, headline, detail, ticker_items):
    """Create a single frame of breaking news animation."""
    width, height = 1080, 1920
    brand_red = hex_to_rgb('#e31837')

    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    # Flash effect at start
    if t < 0.3:
        flash_alpha = 1 - (t / 0.3)
        overlay = Image.new('RGB', (width, height), brand_red)
        canvas = Image.blend(canvas, overlay, flash_alpha * 0.5)
        draw = ImageDraw.Draw(canvas)

    # "BREAKING NEWS" banner at top
    banner_height = 120
    pulse = 0.85 + 0.15 * np.sin(t * 5) if t > 0.5 else 1.0
    banner_color = tuple(int(c * pulse) for c in brand_red)
    draw.rectangle([(0, 150), (width, 150 + banner_height)], fill=banner_color)

    # "BREAKING NEWS" text
    font_breaking = get_font(60, bold=True)
    text = "BREAKING NEWS"
    bbox = draw.textbbox((0, 0), text, font=font_breaking)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 170), text, fill=(255, 255, 255), font=font_breaking)

    # Main headline (appears after 0.5s)
    if t >= 0.5:
        alpha = min(1.0, (t - 0.5) / 0.5)
        font_headline = get_font(70, bold=True)
        color = tuple(int(255 * alpha) for _ in range(3))

        # Word wrap headline
        words = headline.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font_headline)
            if bbox[2] - bbox[0] < width - 100:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y = 350
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_headline)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, y), line, fill=color, font=font_headline)
            y += 90

    # Detail text (appears after 1.5s)
    if t >= 1.5:
        alpha = min(1.0, (t - 1.5) / 0.5)
        font_detail = get_font(40)
        color = tuple(int(200 * alpha) for _ in range(3))

        bbox = draw.textbbox((0, 0), detail, font=font_detail)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 650), detail, fill=color, font=font_detail)

    # Live indicator
    if t >= 1:
        blink = int(t * 2) % 2 == 0
        if blink:
            draw.ellipse([(50, 170), (80, 200)], fill=(255, 0, 0))
            font_live = get_font(30, bold=True)
            draw.text((90, 175), "LIVE", fill=(255, 255, 255), font=font_live)

    # Scrolling ticker at bottom
    ticker_y = 1700
    ticker_height = 80
    draw.rectangle([(0, ticker_y), (width, ticker_y + ticker_height)], fill=(20, 20, 20))

    # Ticker text (scrolling)
    font_ticker = get_font(32)
    ticker_text = "  ///  ".join(ticker_items)
    ticker_text = ticker_text + "  ///  " + ticker_text  # Repeat for seamless scroll

    bbox = draw.textbbox((0, 0), ticker_text, font=font_ticker)
    text_width = bbox[2] - bbox[0]

    # Calculate scroll position
    scroll_speed = 100  # pixels per second
    scroll_x = -(t * scroll_speed) % (text_width // 2)

    draw.text((scroll_x, ticker_y + 20), ticker_text, fill=(255, 255, 255), font=font_ticker)

    # Timestamp
    font_time = get_font(28)
    timestamp = datetime.now().strftime("%I:%M %p ET")
    draw.text((width - 150, ticker_y + 25), timestamp, fill=(150, 150, 150), font=font_time)

    # Center content area - could add chart or image here
    if t >= 2:
        # Placeholder for main visual
        chart_y = 800
        chart_height = 600

        # Draw a simple price chart placeholder
        font_chart = get_font(36)
        draw.text((100, chart_y), "SILVER SPOT PRICE", fill=(136, 136, 136), font=font_chart)

        # Simulated price line
        points = []
        for i in range(50):
            x = 100 + i * 18
            progress = min(1.0, (t - 2) / 3)
            visible_points = int(50 * progress)
            if i <= visible_points:
                # Upward trend with volatility
                base_y = chart_y + 500 - (i * 6)
                noise = np.sin(i * 0.5) * 20
                y = base_y + noise
                points.append((x, y))

        if len(points) > 1:
            for i in range(len(points) - 1):
                green = hex_to_rgb('#4ade80')
                draw.line([points[i], points[i+1]], fill=green, width=4)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_breaking_news(headline=None, detail=None):
    """Generate breaking news video."""
    alert = get_latest_alert()

    if headline is None:
        headline = alert['title'] if alert else "SILVER BREAKS $90"
    if detail is None:
        detail = alert['detail'] if alert else "Highest level since 1980"

    ticker_items = [
        "SILVER +5.3%",
        "CITI -4.5%",
        "VIX 27.6",
        "GOLD $4,243",
        "MS WARNING",
        "RISK INDEX: 5.0"
    ]

    duration = 12
    fps = 30

    print(f"Generating breaking news: {headline}...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, headline, detail, ticker_items)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"breaking_news_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--headline', default=None, help='Custom headline')
    parser.add_argument('--detail', default=None, help='Custom detail')
    args = parser.parse_args()
    generate_breaking_news(args.headline, args.detail)
