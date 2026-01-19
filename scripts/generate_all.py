"""
Master Script: Generate All Videos
Run all video generation scripts or select specific ones.

Usage:
    python generate_all.py              # Generate all videos
    python generate_all.py --list       # List available scripts
    python generate_all.py 1 5 9        # Generate specific scripts by number
    python generate_all.py --quick      # Generate only fast scripts (images)
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Change to scripts directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, '..')

SCRIPTS = {
    1: ('01_silver_breakout', 'Silver Breakout Alert', 'generate_silver_breakout'),
    2: ('02_bank_crisis', 'Bank Crisis Alert', 'generate_bank_crisis'),
    3: ('03_countdown_deadline', 'Countdown Deadline', 'generate_countdown'),
    4: ('04_daily_summary', 'Daily Summary', 'generate_daily_summary'),
    5: ('05_domino_effect', 'Domino Effect', 'generate_domino_video'),
    6: ('06_cascade_stage', 'Cascade Stage', 'generate_cascade_video'),
    7: ('07_risk_meter', 'Risk Meter', 'generate_risk_video'),
    8: ('08_silver_squeeze', 'Silver Squeeze', 'generate_squeeze_video'),
    9: ('09_breaking_news', 'Breaking News', 'generate_breaking_news'),
    10: ('10_bank_comparison', 'Bank Comparison', 'generate_bank_comparison'),
}

def list_scripts():
    """List all available scripts."""
    print("\n=== Available Video Scripts ===\n")
    for num, (module, name, _) in SCRIPTS.items():
        print(f"  {num:2d}. {name}")
    print("\n")

def run_script(num):
    """Run a specific script by number."""
    if num not in SCRIPTS:
        print(f"Error: Script {num} not found")
        return None

    module_name, name, func_name = SCRIPTS[num]
    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print(f"{'='*50}\n")

    try:
        module = __import__(module_name)
        func = getattr(module, func_name)
        path = func()
        return path
    except Exception as e:
        print(f"Error running {name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description='Generate fault.watch videos')
    parser.add_argument('scripts', nargs='*', type=int, help='Script numbers to run (1-10)')
    parser.add_argument('--list', '-l', action='store_true', help='List available scripts')
    parser.add_argument('--all', '-a', action='store_true', help='Generate all videos')
    args = parser.parse_args()

    if args.list:
        list_scripts()
        return

    # Determine which scripts to run
    if args.all or not args.scripts:
        scripts_to_run = list(SCRIPTS.keys())
    else:
        scripts_to_run = args.scripts

    print(f"\n{'#'*60}")
    print(f"# fault.watch Video Generator")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# Scripts: {len(scripts_to_run)}")
    print(f"{'#'*60}")

    generated = []
    failed = []

    for num in scripts_to_run:
        path = run_script(num)
        if path:
            generated.append((num, SCRIPTS[num][1], path))
        else:
            failed.append((num, SCRIPTS[num][1]))

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nSuccessful: {len(generated)}")
    for num, name, path in generated:
        print(f"  [{num:2d}] {name}")
        print(f"       -> {path}")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for num, name in failed:
            print(f"  [{num:2d}] {name}")

    print(f"\nOutput directory: content-output/videos/")
    print()

if __name__ == "__main__":
    main()
