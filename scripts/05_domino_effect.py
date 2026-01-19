"""
Script 5: Domino Effect Visualization
Shows the cascade of falling dominoes as banks fail.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from pathlib import Path
from datetime import datetime
import requests

# Domino sequence (order of potential failures)
DOMINOES = [
    {'id': 'silver_90', 'label': 'Silver $90', 'status': 'FALLEN'},
    {'id': 'ms_warning', 'label': 'MS Warning', 'status': 'WOBBLING'},
    {'id': 'citi_stress', 'label': 'Citi Stress', 'status': 'STANDING'},
    {'id': 'regional_panic', 'label': 'Regional Panic', 'status': 'STANDING'},
    {'id': 'fed_intervention', 'label': 'Fed Steps In', 'status': 'STANDING'},
    {'id': 'silver_150', 'label': 'Silver $150', 'status': 'STANDING'},
    {'id': 'bank_holiday', 'label': 'Bank Holiday', 'status': 'STANDING'},
]

def get_domino_status():
    """Fetch current domino status from API."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        return data.get('dominoes', [])
    except:
        return DOMINOES

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

def draw_domino(draw, x, y, width, height, angle, label, status, alpha=1.0):
    """Draw a single domino piece."""
    colors = {
        'FALLEN': '#e31837',      # Red
        'WOBBLING': '#ff8c42',    # Orange
        'STANDING': '#4ade80',    # Green
        'WARNING': '#fbbf24',     # Yellow
    }
    color = hex_to_rgb(colors.get(status, '#888888'))
    color = tuple(int(c * alpha) for c in color)

    # Simple rectangle representation (angle affects visual)
    if angle > 45:  # Fallen
        # Draw horizontal (fallen)
        draw.rectangle([(x, y + height//2), (x + height, y + height//2 + width//3)], fill=color, outline=(255,255,255))
    elif angle > 15:  # Wobbling
        # Draw tilted (approximate with skewed rectangle)
        points = [(x + angle//2, y), (x + width + angle//2, y), (x + width, y + height), (x, y + height)]
        draw.polygon(points, fill=color, outline=(255,255,255))
    else:  # Standing
        draw.rectangle([(x, y), (x + width, y + height)], fill=color, outline=(255,255,255))

    # Label below domino
    font = get_font(24)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text((x + width//2 - text_width//2, y + height + 10), label, fill=(255,255,255), font=font)

def create_frame(t, duration, dominoes):
    """Create a single frame of the domino animation."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    # Header
    font_header = get_font(70, bold=True)
    font_sub = get_font(36)

    header = "DOMINO EFFECT"
    bbox = draw.textbbox((0, 0), header, font=font_header)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 200), header, fill=(227, 24, 55), font=font_header)

    subtitle = "Banking Crisis Cascade"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 290), subtitle, fill=(136, 136, 136), font=font_sub)

    # Draw dominoes
    domino_width = 80
    domino_height = 200
    start_x = 100
    start_y = 500
    spacing = 130

    for i, domino in enumerate(dominoes):
        x = start_x + i * spacing
        y = start_y

        # Animate falling based on time
        fall_time = i * 0.8  # Each domino falls 0.8s after previous
        if t > fall_time:
            progress = min(1.0, (t - fall_time) / 0.5)
            if domino['status'] == 'FALLEN' or (domino['status'] == 'WOBBLING' and progress > 0.5):
                angle = 90 * progress
            elif domino['status'] == 'WOBBLING':
                angle = 30 * np.sin(t * 5)  # Wobble effect
            else:
                angle = 0
        else:
            angle = 0 if domino['status'] == 'STANDING' else (90 if domino['status'] == 'FALLEN' else 15)

        draw_domino(draw, x, y, domino_width, domino_height, angle, domino['label'], domino['status'])

    # Risk meter at bottom
    font_risk = get_font(48, bold=True)
    fallen_count = sum(1 for d in dominoes if d['status'] == 'FALLEN')
    total = len(dominoes)
    risk_text = f"{fallen_count}/{total} DOMINOES FALLEN"
    bbox = draw.textbbox((0, 0), risk_text, font=font_risk)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 1600), risk_text, fill=(255, 255, 255), font=font_risk)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_domino_video():
    """Generate domino effect visualization video."""
    dominoes = get_domino_status()
    if not dominoes or not isinstance(dominoes[0], dict) or 'label' not in dominoes[0]:
        dominoes = DOMINOES  # Use default if API format different

    duration = 12
    fps = 30

    print("Generating domino effect video...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, dominoes)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"domino_effect_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_domino_video()
