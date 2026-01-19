"""
Compile Daily Content
Combines all videos from a specific date into one compilation video.
Also creates a montage image from all images.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

os.chdir(Path(__file__).parent)
sys.path.insert(0, '..')

from moviepy import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
from PIL import Image

LIBRARY_DIR = Path("../content-library")
OUTPUT_DIR = Path("../content-compilations")

def get_date_content(date_str: str = None):
    """Get all content for a specific date."""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    date_dir = LIBRARY_DIR / date_str

    content = {'videos': [], 'images': [], 'date': date_str}

    if date_dir.exists():
        videos_dir = date_dir / 'videos'
        images_dir = date_dir / 'images'

        if videos_dir.exists():
            content['videos'] = sorted([f for f in videos_dir.iterdir() if f.suffix == '.mp4'])
        if images_dir.exists():
            content['images'] = sorted([f for f in images_dir.iterdir() if f.suffix == '.png'])

    return content

def compile_videos(date_str: str = None, add_transitions: bool = True) -> Optional[Path]:
    """Compile all videos from a date into one video."""
    content = get_date_content(date_str)

    if not content['videos']:
        print(f"No videos found for {content['date']}")
        return None

    print(f"\n=== Compiling Videos for {content['date']} ===")
    print(f"Found {len(content['videos'])} videos")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    clips = []
    for video_path in content['videos']:
        print(f"  Adding: {video_path.name}")
        try:
            clip = VideoFileClip(str(video_path))
            clips.append(clip)

            # Add 0.5s black transition between clips
            if add_transitions and video_path != content['videos'][-1]:
                black = ImageClip(
                    size=(1080, 1920),
                    color=(0, 0, 0)
                ).with_duration(0.5)
                clips.append(black)
        except Exception as e:
            print(f"    Error loading: {e}")

    if not clips:
        print("No valid clips to compile")
        return None

    # Concatenate all clips
    print("\nConcatenating clips...")
    final = concatenate_videoclips(clips, method="compose")

    # Output path
    output_path = OUTPUT_DIR / f"daily_compilation_{content['date']}.mp4"

    print(f"Writing to: {output_path}")
    final.write_videofile(
        str(output_path),
        fps=30,
        codec='libx264',
        audio_codec='aac',
        logger=None
    )

    # Clean up
    final.close()
    for clip in clips:
        clip.close()

    print(f"\nCompilation complete: {output_path}")
    print(f"Duration: {final.duration:.1f} seconds")
    return output_path

def create_image_montage(date_str: str = None, cols: int = 2) -> Optional[Path]:
    """Create a montage of all images from a date."""
    content = get_date_content(date_str)

    if not content['images']:
        print(f"No images found for {content['date']}")
        return None

    print(f"\n=== Creating Image Montage for {content['date']} ===")
    print(f"Found {len(content['images'])} images")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load images
    images = []
    for img_path in content['images']:
        try:
            img = Image.open(img_path)
            images.append(img)
            print(f"  Added: {img_path.name}")
        except Exception as e:
            print(f"  Error loading {img_path.name}: {e}")

    if not images:
        return None

    # Calculate montage size
    img_width, img_height = images[0].size
    rows = (len(images) + cols - 1) // cols

    # Create montage (scaled down)
    scale = 0.5
    thumb_w = int(img_width * scale)
    thumb_h = int(img_height * scale)

    montage_width = thumb_w * cols
    montage_height = thumb_h * rows

    montage = Image.new('RGB', (montage_width, montage_height), (13, 13, 13))

    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        x = col * thumb_w
        y = row * thumb_h

        # Resize and paste
        thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        montage.paste(thumb, (x, y))

    # Save montage
    output_path = OUTPUT_DIR / f"daily_montage_{content['date']}.png"
    montage.save(output_path, 'PNG')

    print(f"\nMontage saved: {output_path}")
    print(f"Size: {montage_width}x{montage_height}")
    return output_path

def list_available_dates():
    """List all dates with content."""
    if not LIBRARY_DIR.exists():
        print("No content library found.")
        return []

    dates = []
    for date_dir in sorted(LIBRARY_DIR.iterdir(), reverse=True):
        if date_dir.is_dir():
            content = get_date_content(date_dir.name)
            video_count = len(content['videos'])
            image_count = len(content['images'])
            if video_count > 0 or image_count > 0:
                dates.append((date_dir.name, video_count, image_count))
                print(f"  {date_dir.name}: {video_count} videos, {image_count} images")

    return dates

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Compile daily content')
    parser.add_argument('--date', '-d', help='Date to compile (YYYY-MM-DD), defaults to today')
    parser.add_argument('--list', '-l', action='store_true', help='List available dates')
    parser.add_argument('--video', '-v', action='store_true', help='Compile video only')
    parser.add_argument('--montage', '-m', action='store_true', help='Create montage only')
    args = parser.parse_args()

    if args.list:
        print("\n=== Available Dates ===\n")
        list_available_dates()
    elif args.video:
        compile_videos(args.date)
    elif args.montage:
        create_image_montage(args.date)
    else:
        # Do both
        compile_videos(args.date)
        create_image_montage(args.date)
