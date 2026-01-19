"""
Organize Content by Date
Moves generated videos and images into dated folders for easy compilation.

Structure:
    content-library/
        2026-01-14/
            videos/
            images/
        2026-01-15/
            ...
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import re

# Paths
SOURCE_DIR = Path("../content-output")
LIBRARY_DIR = Path("../content-library")

def get_file_date(filename):
    """Extract date from filename (format: type_YYYYMMDD_HHMMSS.ext)"""
    match = re.search(r'_(\d{8})_', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')

def organize_content():
    """Move all content to dated folders."""

    # Create library directory
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    moved_count = {'images': 0, 'videos': 0}

    for content_type in ['images', 'videos']:
        source_path = SOURCE_DIR / content_type
        if not source_path.exists():
            continue

        for file in source_path.iterdir():
            if file.is_file() and not file.name.startswith('.'):
                # Get date from filename
                date_folder = get_file_date(file.name)

                # Create dated folder structure
                dest_dir = LIBRARY_DIR / date_folder / content_type
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Move file
                dest_path = dest_dir / file.name
                if not dest_path.exists():
                    shutil.move(str(file), str(dest_path))
                    moved_count[content_type] += 1
                    print(f"  Moved: {file.name} -> {date_folder}/{content_type}/")
                else:
                    print(f"  Skipped (exists): {file.name}")

    return moved_count

def list_library():
    """List all content in the library."""
    if not LIBRARY_DIR.exists():
        print("No content library found.")
        return

    print("\n=== Content Library ===\n")

    for date_folder in sorted(LIBRARY_DIR.iterdir(), reverse=True):
        if date_folder.is_dir():
            print(f"{date_folder.name}/")

            for content_type in ['videos', 'images']:
                type_dir = date_folder / content_type
                if type_dir.exists():
                    files = list(type_dir.iterdir())
                    print(f"  {content_type}/ ({len(files)} files)")
                    for f in sorted(files)[:5]:  # Show first 5
                        print(f"    - {f.name}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more")
            print()

def get_today_content():
    """Get paths to today's content for video compilation."""
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = LIBRARY_DIR / today

    content = {'videos': [], 'images': []}

    if today_dir.exists():
        for content_type in ['videos', 'images']:
            type_dir = today_dir / content_type
            if type_dir.exists():
                content[content_type] = sorted(type_dir.iterdir())

    return content

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', action='store_true', help='List library contents')
    parser.add_argument('--today', '-t', action='store_true', help='Show today\'s content')
    args = parser.parse_args()

    if args.list:
        list_library()
    elif args.today:
        content = get_today_content()
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n=== Today's Content ({today}) ===\n")
        print(f"Videos: {len(content['videos'])}")
        for v in content['videos']:
            print(f"  - {v.name}")
        print(f"\nImages: {len(content['images'])}")
        for i in content['images']:
            print(f"  - {i.name}")
    else:
        print("\n=== Organizing Content ===\n")
        counts = organize_content()
        print(f"\nMoved {counts['videos']} videos, {counts['images']} images")
        print(f"Library location: {LIBRARY_DIR.absolute()}")
