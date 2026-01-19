"""
Script 7: Risk Meter Alert
Animated risk gauge showing current crisis probability.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from pathlib import Path
from datetime import datetime
import requests
import math

def get_risk_data():
    """Fetch risk index from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        return {
            'risk_index': data.get('risk_index', 5.0),
            'risk_label': data.get('risk_label', 'WARNING'),
            'stress_level': data.get('stress_level', 5.0)
        }
    except:
        return {'risk_index': 5.0, 'risk_label': 'WARNING', 'stress_level': 5.0}

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

def draw_gauge(draw, cx, cy, radius, value, max_value=10):
    """Draw a semi-circular gauge."""
    # Background arc (gray)
    start_angle = 180
    end_angle = 360

    # Draw tick marks
    for i in range(11):
        angle = math.radians(180 + i * 18)  # 180 degrees spread
        inner_r = radius - 20
        outer_r = radius + 10

        x1 = cx + inner_r * math.cos(angle)
        y1 = cy + inner_r * math.sin(angle)
        x2 = cx + outer_r * math.cos(angle)
        y2 = cy + outer_r * math.sin(angle)

        color = (100, 100, 100)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=3)

    # Colored sections
    sections = [
        (0, 3, '#4ade80'),    # Green (safe)
        (3, 5, '#fbbf24'),    # Yellow (caution)
        (5, 7, '#ff8c42'),    # Orange (warning)
        (7, 10, '#e31837'),   # Red (critical)
    ]

    for start, end, color in sections:
        start_a = 180 + (start / max_value) * 180
        end_a = 180 + (end / max_value) * 180
        rgb = hex_to_rgb(color)
        draw.arc([(cx - radius, cy - radius), (cx + radius, cy + radius)],
                 start_a, end_a, fill=rgb, width=25)

    # Needle
    needle_angle = math.radians(180 + (value / max_value) * 180)
    needle_length = radius - 40
    nx = cx + needle_length * math.cos(needle_angle)
    ny = cy + needle_length * math.sin(needle_angle)

    # Needle shadow
    draw.line([(cx + 2, cy + 2), (nx + 2, ny + 2)], fill=(50, 50, 50), width=8)
    # Needle
    draw.line([(cx, cy), (nx, ny)], fill=(255, 255, 255), width=6)
    # Center cap
    draw.ellipse([(cx - 15, cy - 15), (cx + 15, cy + 15)], fill=(200, 200, 200))

def create_frame(t, duration, risk_data):
    """Create a single frame of the risk meter animation."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    target_risk = risk_data['risk_index']

    # Animate needle from 0 to target
    if t < 3:
        current_risk = target_risk * (t / 3) ** 0.5  # Ease out
    else:
        # Slight wobble at rest
        wobble = 0.1 * np.sin(t * 2)
        current_risk = target_risk + wobble

    # Header
    font_header = get_font(60, bold=True)
    header = "RISK INDEX"
    bbox = draw.textbbox((0, 0), header, font=font_header)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 200), header, fill=(255, 255, 255), font=font_header)

    # Draw gauge
    draw_gauge(draw, width // 2, 650, 300, current_risk)

    # Risk value (big number)
    font_value = get_font(200, bold=True)
    if target_risk >= 7:
        value_color = hex_to_rgb('#e31837')
    elif target_risk >= 5:
        value_color = hex_to_rgb('#ff8c42')
    elif target_risk >= 3:
        value_color = hex_to_rgb('#fbbf24')
    else:
        value_color = hex_to_rgb('#4ade80')

    # Pulse effect for high risk
    if target_risk >= 7:
        pulse = 0.7 + 0.3 * np.sin(t * 4)
        value_color = tuple(int(c * pulse) for c in value_color)

    value_text = f"{current_risk:.1f}"
    bbox = draw.textbbox((0, 0), value_text, font=font_value)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 850), value_text, fill=value_color, font=font_value)

    # Risk label
    font_label = get_font(70, bold=True)
    label = risk_data['risk_label']
    bbox = draw.textbbox((0, 0), label, font=font_label)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 1100), label, fill=value_color, font=font_label)

    # Scale labels
    font_scale = get_font(30)
    labels = [('SAFE', 150), ('CAUTION', 350), ('WARNING', 600), ('CRITICAL', 850)]
    for label_text, x_offset in labels:
        draw.text((x_offset, 950), label_text, fill=(100, 100, 100), font=font_scale)

    # Explanation text
    if t > 4:
        alpha = min(1.0, (t - 4) / 1)
        font_explain = get_font(32)
        explanations = [
            "Based on silver price, bank stress,",
            "VIX levels, and short positions"
        ]
        for i, line in enumerate(explanations):
            color = tuple(int(136 * alpha) for _ in range(3))
            bbox = draw.textbbox((0, 0), line, font=font_explain)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, 1250 + i * 45), line, fill=color, font=font_explain)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_risk_video():
    """Generate risk meter visualization video."""
    risk_data = get_risk_data()

    duration = 10
    fps = 30

    print(f"Generating risk meter video (Risk: {risk_data['risk_index']})...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, risk_data)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"risk_meter_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_risk_video()
