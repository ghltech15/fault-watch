"""
Script 8: Silver Squeeze Alert
Dramatic visualization of the silver short squeeze thesis.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from pathlib import Path
from datetime import datetime
import requests

def get_squeeze_data():
    """Fetch naked short data from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/naked-shorts", timeout=10)
        data = r.json()
        return {
            'total_short_oz': data.get('total_short_oz', 30e9),
            'physical_available': data.get('physical_available_oz', 1e9),
            'ratio': data.get('ratio', 30),
            'price': 91.57
        }
    except:
        return {'total_short_oz': 30e9, 'physical_available': 1e9, 'ratio': 30, 'price': 91.57}

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

def format_billions(value):
    """Format large numbers as billions."""
    return f"{value / 1e9:.1f}B oz"

def create_frame(t, duration, data):
    """Create a single frame of the silver squeeze animation."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    brand_red = hex_to_rgb('#e31837')

    # Flash effect at start
    if t < 0.5:
        flash_alpha = 1 - (t / 0.5)
        overlay = Image.new('RGB', (width, height), brand_red)
        canvas = Image.blend(canvas, overlay, flash_alpha * 0.3)
        draw = ImageDraw.Draw(canvas)

    # Header - "SILVER SQUEEZE"
    if t >= 0.3:
        alpha = min(1.0, (t - 0.3) / 0.5)
        font_header = get_font(80, bold=True)
        color = tuple(int(c * alpha) for c in brand_red)
        header = "SILVER SQUEEZE"
        bbox = draw.textbbox((0, 0), header, font=font_header)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 200), header, fill=color, font=font_header)

    # Subtitle
    if t >= 0.8:
        alpha = min(1.0, (t - 0.8) / 0.5)
        font_sub = get_font(36)
        color = tuple(int(136 * alpha) for _ in range(3))
        subtitle = "The Largest Naked Short in History"
        bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 300), subtitle, fill=color, font=font_sub)

    # Animated ratio counter
    if t >= 1.5:
        target_ratio = data['ratio']
        if t < 4:
            progress = (t - 1.5) / 2.5
            current_ratio = int(target_ratio * progress)
        else:
            current_ratio = target_ratio
            # Pulse effect
            pulse = 0.8 + 0.2 * np.sin(t * 3)
            brand_red = tuple(int(c * pulse) for c in hex_to_rgb('#e31837'))

        font_ratio = get_font(250, bold=True)
        ratio_text = f"{current_ratio}:1"
        bbox = draw.textbbox((0, 0), ratio_text, font=font_ratio)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 420), ratio_text, fill=brand_red, font=font_ratio)

        # Explanation
        font_explain = get_font(40)
        explain = "Paper Silver to Physical"
        bbox = draw.textbbox((0, 0), explain, font=font_explain)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, 720), explain, fill=(200, 200, 200), font=font_explain)

    # Stats boxes
    if t >= 4:
        alpha = min(1.0, (t - 4) / 1)
        font_label = get_font(30)
        font_value = get_font(50, bold=True)

        # Paper silver sold
        box1_y = 850
        color_label = tuple(int(136 * alpha) for _ in range(3))
        color_value = tuple(int(255 * alpha) for _ in range(3))

        draw.text((100, box1_y), "PAPER SILVER SOLD", fill=color_label, font=font_label)
        draw.text((100, box1_y + 40), format_billions(data['total_short_oz']), fill=color_value, font=font_value)

    if t >= 4.5:
        alpha = min(1.0, (t - 4.5) / 1)
        # Physical available
        box2_y = 1000
        color_label = tuple(int(136 * alpha) for _ in range(3))
        color_value = tuple(int(255 * alpha) for _ in range(3))

        draw.text((100, box2_y), "PHYSICAL AVAILABLE", fill=color_label, font=font_label)
        draw.text((100, box2_y + 40), format_billions(data['physical_available']), fill=color_value, font=font_value)

    if t >= 5:
        alpha = min(1.0, (t - 5) / 1)
        # Visual comparison bar
        bar_y = 1180
        bar_height = 60
        full_width = 900

        # Physical (small)
        physical_width = int(full_width / data['ratio'])
        green = tuple(int(c * alpha) for c in hex_to_rgb('#4ade80'))
        draw.rectangle([(90, bar_y), (90 + physical_width, bar_y + bar_height)], fill=green)

        # Paper (full width) - animate growth
        if t < 7:
            paper_progress = (t - 5) / 2
            paper_width = int(full_width * paper_progress)
        else:
            paper_width = full_width

        red = tuple(int(c * alpha) for c in brand_red)
        draw.rectangle([(90, bar_y + bar_height + 20), (90 + paper_width, bar_y + bar_height * 2 + 20)], fill=red)

        # Labels
        font_bar = get_font(24)
        draw.text((90, bar_y + bar_height + 85), "Physical", fill=green, font=font_bar)
        draw.text((90 + paper_width - 50, bar_y + bar_height + 85), "Paper", fill=red, font=font_bar)

    # Bottom message
    if t >= 7:
        alpha = min(1.0, (t - 7) / 1)
        font_msg = get_font(36, bold=True)
        msg_color = tuple(int(c * alpha) for c in brand_red)

        messages = [
            "When they demand delivery...",
            "There won't be enough silver."
        ]
        for i, msg in enumerate(messages):
            bbox = draw.textbbox((0, 0), msg, font=font_msg)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, 1450 + i * 60), msg, fill=msg_color, font=font_msg)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_squeeze_video():
    """Generate silver squeeze visualization video."""
    data = get_squeeze_data()

    duration = 12
    fps = 30

    print("Generating silver squeeze video...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, data)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"silver_squeeze_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_squeeze_video()
