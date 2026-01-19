"""
Script 6: Cascade Stage Alert
Shows which stage of the banking cascade we're currently in.
"""
import sys
sys.path.insert(0, '..')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from pathlib import Path
from datetime import datetime
import requests

# Cascade stages
STAGES = [
    {'stage': 1, 'name': 'ACCUMULATION', 'range': '$25-35', 'status': 'complete', 'color': '#4ade80'},
    {'stage': 2, 'name': 'AWAKENING', 'range': '$35-50', 'status': 'complete', 'color': '#4ade80'},
    {'stage': 3, 'name': 'STRESS TEST', 'range': '$50-75', 'status': 'complete', 'color': '#4ade80'},
    {'stage': 4, 'name': 'WARNING SIGNS', 'range': '$75-100', 'status': 'active', 'color': '#ff8c42'},
    {'stage': 5, 'name': 'MARGIN CALLS', 'range': '$100-150', 'status': 'pending', 'color': '#888888'},
    {'stage': 6, 'name': 'BANK FAILURES', 'range': '$150-200', 'status': 'pending', 'color': '#888888'},
    {'stage': 7, 'name': 'SYSTEMIC CRISIS', 'range': '$200+', 'status': 'pending', 'color': '#888888'},
]

def get_current_stage():
    """Determine current stage from silver price."""
    try:
        r = requests.get("https://fault-watch-api.fly.dev/api/dashboard", timeout=10)
        data = r.json()
        silver = data['prices'].get('silver', {}).get('price', 30)

        if silver >= 200: return 7
        elif silver >= 150: return 6
        elif silver >= 100: return 5
        elif silver >= 75: return 4
        elif silver >= 50: return 3
        elif silver >= 35: return 2
        else: return 1
    except:
        return 4  # Default to stage 4

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

def create_frame(t, duration, current_stage):
    """Create a single frame of the cascade stage animation."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), (13, 13, 13))
    draw = ImageDraw.Draw(canvas)

    # Header with pulse effect on "STAGE X"
    font_header = get_font(50, bold=True)
    font_stage = get_font(180, bold=True)
    font_name = get_font(60, bold=True)

    header = "CASCADE STAGE"
    bbox = draw.textbbox((0, 0), header, font=font_header)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 200), header, fill=(136, 136, 136), font=font_header)

    # Giant stage number with pulse
    pulse = 0.8 + 0.2 * np.sin(t * 3)
    stage_color = tuple(int(c * pulse) for c in hex_to_rgb('#ff8c42'))
    stage_text = str(current_stage)
    bbox = draw.textbbox((0, 0), stage_text, font=font_stage)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 280), stage_text, fill=stage_color, font=font_stage)

    # Stage name
    stage_info = STAGES[current_stage - 1]
    bbox = draw.textbbox((0, 0), stage_info['name'], font=font_name)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 500), stage_info['name'], fill=(255, 255, 255), font=font_name)

    # Price range
    font_range = get_font(36)
    range_text = f"Silver: {stage_info['range']}"
    bbox = draw.textbbox((0, 0), range_text, font=font_range)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 580), range_text, fill=(136, 136, 136), font=font_range)

    # Progress bar showing all stages
    bar_y = 720
    bar_height = 40
    bar_margin = 60

    for i, stage in enumerate(STAGES):
        stage_appear_time = i * 0.3
        if t < stage_appear_time:
            continue

        alpha = min(1.0, (t - stage_appear_time) / 0.3)
        x1 = bar_margin + i * ((width - 2*bar_margin) // len(STAGES))
        x2 = bar_margin + (i + 1) * ((width - 2*bar_margin) // len(STAGES)) - 5

        color = hex_to_rgb(stage['color'])
        color = tuple(int(c * alpha) for c in color)

        # Highlight current stage
        if i + 1 == current_stage:
            # Pulsing border for current stage
            border_alpha = 0.5 + 0.5 * np.sin(t * 4)
            border_color = tuple(int(255 * border_alpha) for _ in range(3))
            draw.rectangle([(x1-3, bar_y-3), (x2+3, bar_y + bar_height+3)], outline=border_color, width=2)

        draw.rectangle([(x1, bar_y), (x2, bar_y + bar_height)], fill=color)

        # Stage number below bar
        font_num = get_font(24)
        num_text = str(i + 1)
        draw.text((x1 + 20, bar_y + bar_height + 10), num_text, fill=(136, 136, 136), font=font_num)

    # Stage list
    list_y = 900
    font_list = get_font(32)
    font_list_bold = get_font(32, bold=True)

    for i, stage in enumerate(STAGES):
        item_appear_time = 2 + i * 0.2
        if t < item_appear_time:
            continue

        alpha = min(1.0, (t - item_appear_time) / 0.2)
        y = list_y + i * 80

        # Status indicator
        color = hex_to_rgb(stage['color'])
        color = tuple(int(c * alpha) for c in color)
        draw.ellipse([(80, y + 5), (100, y + 25)], fill=color)

        # Stage info
        text_color = tuple(int(255 * alpha) for _ in range(3))
        if i + 1 == current_stage:
            draw.text((120, y), f"Stage {stage['stage']}: {stage['name']}", fill=color, font=font_list_bold)
        else:
            gray = tuple(int(136 * alpha) for _ in range(3))
            draw.text((120, y), f"Stage {stage['stage']}: {stage['name']}", fill=gray, font=font_list)

        # Price range on right
        draw.text((800, y), stage['range'], fill=tuple(int(100 * alpha) for _ in range(3)), font=font_list)

    # Watermark
    font_wm = get_font(24)
    draw.text((width//2 - 50, height - 60), "fault.watch", fill=(136, 136, 136), font=font_wm)

    return np.array(canvas)

def generate_cascade_video():
    """Generate cascade stage visualization video."""
    current_stage = get_current_stage()

    duration = 10
    fps = 30

    print(f"Generating cascade stage video (Stage {current_stage})...")
    frames = []
    for frame_num in range(int(duration * fps)):
        t = frame_num / fps
        frame = create_frame(t, duration, current_stage)
        frames.append(frame)

    clips = [ImageClip(frame).with_duration(1/fps).with_start(i/fps) for i, frame in enumerate(frames)]
    video = concatenate_videoclips(clips, method="compose")

    output_dir = Path("../content-output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"cascade_stage_{timestamp}.mp4"

    video.write_videofile(str(output_path), fps=fps, codec='libx264', audio_codec='aac', logger=None)
    video.close()

    print(f"Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_cascade_video()
