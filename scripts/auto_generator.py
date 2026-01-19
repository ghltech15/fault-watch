"""
Auto Content Generator
Automatically generates videos based on:
- Scheduled times (morning/afternoon)
- Price alerts (silver breakouts, bank crashes)

Run this script to start monitoring, or use Windows Task Scheduler.
"""
import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List

# Change to scripts directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, '..')

# Import generators
from organize_content import organize_content

# Configuration
@dataclass
class AutoGenConfig:
    # Scheduled generation times (24h format)
    morning_time: str = "09:30"
    afternoon_time: str = "16:00"
    evening_time: str = "21:00"

    # Alert thresholds
    silver_alert_levels: List[float] = None
    bank_drop_threshold: float = -5.0  # Alert if bank drops more than 5%
    vix_alert_level: float = 30.0

    # Cooldown (don't re-alert within this many hours)
    alert_cooldown_hours: float = 2.0

    # API endpoint
    api_url: str = "https://fault-watch-api.fly.dev/api/dashboard"

    def __post_init__(self):
        if self.silver_alert_levels is None:
            self.silver_alert_levels = [90, 95, 100, 110, 125, 150]

CONFIG = AutoGenConfig()

# Track last alert times
LAST_ALERTS: Dict[str, datetime] = {}
LAST_SCHEDULED: Dict[str, str] = {}

def log(msg: str):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def can_alert(alert_key: str) -> bool:
    """Check if we can fire an alert (respects cooldown)."""
    if alert_key not in LAST_ALERTS:
        return True
    elapsed = datetime.now() - LAST_ALERTS[alert_key]
    return elapsed > timedelta(hours=CONFIG.alert_cooldown_hours)

def record_alert(alert_key: str):
    """Record that an alert was fired."""
    LAST_ALERTS[alert_key] = datetime.now()

def fetch_market_data() -> Optional[Dict]:
    """Fetch current market data from API."""
    try:
        r = requests.get(CONFIG.api_url, timeout=15)
        return r.json()
    except Exception as e:
        log(f"API error: {e}")
        return None

def run_generator(script_num: int, description: str):
    """Run a specific generator script."""
    log(f"Generating: {description}")
    try:
        from generate_all import run_script
        path = run_script(script_num)
        if path:
            log(f"  Created: {path}")
            # Organize into dated folder
            organize_content()
        return path
    except Exception as e:
        log(f"  Error: {e}")
        return None

def check_scheduled_generation():
    """Check if it's time for scheduled generation."""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    schedules = [
        (CONFIG.morning_time, "morning", [1, 4, 7]),      # Silver, Daily, Risk
        (CONFIG.afternoon_time, "afternoon", [4, 6, 10]), # Daily, Cascade, Banks
        (CONFIG.evening_time, "evening", [4, 5, 9]),      # Daily, Domino, Breaking
    ]

    for scheduled_time, period, scripts in schedules:
        schedule_key = f"{period}_{today}"

        # Check if within 1 minute of scheduled time
        if current_time == scheduled_time and schedule_key not in LAST_SCHEDULED:
            log(f"=== Scheduled {period.upper()} generation ===")
            LAST_SCHEDULED[schedule_key] = current_time

            for script_num in scripts:
                run_generator(script_num, f"Scheduled {period} #{script_num}")

            return True

    return False

def check_alert_triggers(data: Dict):
    """Check for alert conditions and generate content."""
    if not data or 'prices' not in data:
        return

    prices = data['prices']
    alerts_fired = []

    # 1. Silver price alerts
    silver = prices.get('silver', {})
    silver_price = silver.get('price', 0)
    silver_change = silver.get('change_pct', 0)

    for level in CONFIG.silver_alert_levels:
        alert_key = f"silver_{level}"
        if silver_price >= level and can_alert(alert_key):
            log(f"!!! SILVER ALERT: ${silver_price:.2f} crossed ${level} !!!")
            run_generator(1, f"Silver breakout ${level}")
            run_generator(8, "Silver squeeze context")
            record_alert(alert_key)
            alerts_fired.append(f"Silver ${level}")

    # 2. Bank crash alerts
    banks = {
        'morgan_stanley': ('Morgan Stanley', 2),
        'citigroup': ('Citigroup', 2),
        'bank_of_america': ('Bank of America', 2),
        'goldman': ('Goldman Sachs', 2),
    }

    for key, (name, script) in banks.items():
        bank_data = prices.get(key, {})
        change = bank_data.get('change_pct', 0)

        if change <= CONFIG.bank_drop_threshold:
            alert_key = f"bank_{key}_{int(change)}"
            if can_alert(alert_key):
                log(f"!!! BANK ALERT: {name} down {change:.1f}% !!!")
                # Run bank crisis with specific bank
                from importlib import import_module
                try:
                    bank_script = import_module('02_bank_crisis')
                    bank_script.generate_bank_crisis(key)
                    organize_content()
                except Exception as e:
                    log(f"  Error: {e}")
                run_generator(10, "Bank comparison")
                record_alert(alert_key)
                alerts_fired.append(f"{name} crash")

    # 3. VIX spike alert
    vix = prices.get('vix_futures', {}).get('price', 0)
    if vix >= CONFIG.vix_alert_level:
        alert_key = f"vix_{int(vix)}"
        if can_alert(alert_key):
            log(f"!!! VIX ALERT: {vix:.1f} !!!")
            run_generator(9, f"Breaking news: VIX {vix:.0f}")
            run_generator(7, "Risk meter update")
            record_alert(alert_key)
            alerts_fired.append(f"VIX {vix:.0f}")

    # 4. Risk index critical
    risk = data.get('risk_index', 0)
    if risk >= 7:
        alert_key = f"risk_{int(risk)}"
        if can_alert(alert_key):
            log(f"!!! RISK ALERT: {risk:.1f} (CRITICAL) !!!")
            run_generator(7, "Risk meter critical")
            run_generator(5, "Domino effect")
            run_generator(6, "Cascade stage")
            record_alert(alert_key)
            alerts_fired.append(f"Risk {risk:.1f}")

    if alerts_fired:
        log(f"Alerts fired: {', '.join(alerts_fired)}")

def run_once():
    """Run a single check cycle."""
    log("Checking market conditions...")

    # Check scheduled generation
    check_scheduled_generation()

    # Fetch and check alerts
    data = fetch_market_data()
    if data:
        check_alert_triggers(data)
        log(f"Risk Index: {data.get('risk_index', 'N/A')}")

def run_continuous(interval_seconds: int = 60):
    """Run continuous monitoring."""
    log("=" * 50)
    log("fault.watch Auto Generator Started")
    log(f"Checking every {interval_seconds} seconds")
    log(f"Morning: {CONFIG.morning_time}, Afternoon: {CONFIG.afternoon_time}, Evening: {CONFIG.evening_time}")
    log("=" * 50)

    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            log("Shutting down...")
            break
        except Exception as e:
            log(f"Error: {e}")

        time.sleep(interval_seconds)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Auto content generator')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--test-alerts', action='store_true', help='Test alert generation')
    args = parser.parse_args()

    if args.test_alerts:
        log("Testing alert generation...")
        run_generator(1, "Test: Silver breakout")
        run_generator(7, "Test: Risk meter")
        run_generator(9, "Test: Breaking news")
    elif args.once:
        run_once()
    else:
        run_continuous(args.interval)
