"""
Content Trigger System for fault.watch
Manages automatic and manual content generation triggers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from content_generator import ContentGenerator, TemplateType, VideoConfig


@dataclass
class TriggerConfig:
    """Configuration for content triggers."""
    price_thresholds: Dict[str, List[float]] = field(default_factory=lambda: {
        'silver': [90, 100, 150],  # Generate at these silver prices
        'ms_drop': [-5, -10, -15],  # MS stock % drops
        'vix': [30, 40, 50],  # VIX spikes
    })
    scheduled_times: List[str] = field(default_factory=lambda: ['09:30', '16:00', '21:00'])
    enabled: bool = True
    cooldown_hours: float = 1.0  # Don't re-trigger same threshold within this time
    generate_video: bool = False  # Default to image-only for speed


class TriggerManager:
    """
    Manages content generation triggers.

    Supports:
    - Price-based triggers (silver price, MS drop %, VIX levels)
    - Scheduled triggers (daily at configured times)
    - Manual triggers (on-demand generation)
    """

    def __init__(self, generator: ContentGenerator = None, config: TriggerConfig = None):
        self.generator = generator or ContentGenerator()
        self.config = config or TriggerConfig()
        self._last_triggered: Dict[str, datetime] = {}
        self._generated_files: List[Path] = []

    def _get_trigger_key(self, trigger_type: str, threshold: float) -> str:
        """Generate unique key for a trigger."""
        return f"{trigger_type}_{threshold}"

    def _can_trigger(self, trigger_key: str) -> bool:
        """Check if trigger can fire (respects cooldown)."""
        if not self.config.enabled:
            return False

        if trigger_key not in self._last_triggered:
            return True

        last_time = self._last_triggered[trigger_key]
        cooldown = timedelta(hours=self.config.cooldown_hours)
        return datetime.now() - last_time > cooldown

    def _record_trigger(self, trigger_key: str) -> None:
        """Record that a trigger fired."""
        self._last_triggered[trigger_key] = datetime.now()

    def check_price_triggers(self, prices: Dict[str, float]) -> List[Path]:
        """
        Check price-based triggers and generate content if thresholds crossed.

        Args:
            prices: Dictionary with keys 'silver', 'ms_change', 'vix'

        Returns:
            List of paths to generated content files
        """
        generated = []

        if not self.config.enabled:
            return generated

        # Check silver price thresholds
        silver_price = prices.get('silver', 0)
        for threshold in self.config.price_thresholds.get('silver', []):
            trigger_key = self._get_trigger_key('silver', threshold)
            if silver_price >= threshold and self._can_trigger(trigger_key):
                path = self._generate_price_alert(
                    asset='SILVER',
                    price=silver_price,
                    change=prices.get('silver_change', 0),
                    threshold=threshold
                )
                if path:
                    generated.append(path)
                    self._record_trigger(trigger_key)

        # Check MS drop thresholds
        ms_change = prices.get('ms_change', 0)
        for threshold in self.config.price_thresholds.get('ms_drop', []):
            trigger_key = self._get_trigger_key('ms_drop', threshold)
            if ms_change <= threshold and self._can_trigger(trigger_key):
                path = self._generate_bank_crisis(
                    bank='Morgan Stanley',
                    price=prices.get('ms_price', 0),
                    change=ms_change,
                    threshold=threshold
                )
                if path:
                    generated.append(path)
                    self._record_trigger(trigger_key)

        # Check VIX thresholds
        vix = prices.get('vix', 0)
        for threshold in self.config.price_thresholds.get('vix', []):
            trigger_key = self._get_trigger_key('vix', threshold)
            if vix >= threshold and self._can_trigger(trigger_key):
                path = self._generate_price_alert(
                    asset='VIX',
                    price=vix,
                    change=prices.get('vix_change', 0),
                    threshold=threshold
                )
                if path:
                    generated.append(path)
                    self._record_trigger(trigger_key)

        self._generated_files.extend(generated)
        return generated

    def check_scheduled_triggers(self) -> Optional[Path]:
        """
        Check if current time matches scheduled trigger times.

        Returns:
            Path to generated file if triggered, None otherwise
        """
        if not self.config.enabled:
            return None

        now = datetime.now()
        current_time = now.strftime('%H:%M')

        for scheduled_time in self.config.scheduled_times:
            trigger_key = f"scheduled_{scheduled_time}_{now.date()}"

            # Check if we're within 1 minute of scheduled time
            if current_time == scheduled_time and self._can_trigger(trigger_key):
                # Generate daily summary
                path = self.manual_generate(TemplateType.DAILY_SUMMARY, {})
                if path:
                    self._record_trigger(trigger_key)
                    return path

        return None

    def manual_generate(
        self,
        template: TemplateType,
        data: Dict[str, Any],
        generate_video: bool = None
    ) -> Path:
        """
        Generate content on-demand.

        Args:
            template: Template type to generate
            data: Data for the template
            generate_video: Override config setting for video generation

        Returns:
            Path to generated file
        """
        should_video = generate_video if generate_video is not None else self.config.generate_video

        if should_video:
            config = VideoConfig(duration=10, fps=30)
            path = self.generator.generate_video(data, template, config)
        else:
            path = self.generator.generate_image(data, template)

        self._generated_files.append(path)
        return path

    def _generate_price_alert(
        self,
        asset: str,
        price: float,
        change: float,
        threshold: float
    ) -> Optional[Path]:
        """Generate a price alert for threshold crossing."""
        data = {
            'asset': asset,
            'price': price,
            'change': change,
        }
        return self.manual_generate(TemplateType.PRICE_ALERT, data)

    def _generate_bank_crisis(
        self,
        bank: str,
        price: float,
        change: float,
        threshold: float
    ) -> Optional[Path]:
        """Generate a bank crisis alert."""
        data = {
            'bank': bank,
            'price': price,
            'change': change,
            'exposure': '$18.5B',  # TODO: Get from actual data
            'loss': '',
        }
        return self.manual_generate(TemplateType.BANK_CRISIS, data)

    def get_trigger_status(self) -> Dict[str, Any]:
        """
        Get current status of all triggers.

        Returns:
            Dictionary with trigger status information
        """
        now = datetime.now()

        # Calculate time until next scheduled trigger
        next_scheduled = None
        for time_str in sorted(self.config.scheduled_times):
            hour, minute = map(int, time_str.split(':'))
            scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if scheduled > now:
                next_scheduled = scheduled
                break

        if next_scheduled is None and self.config.scheduled_times:
            # Next scheduled is tomorrow
            time_str = sorted(self.config.scheduled_times)[0]
            hour, minute = map(int, time_str.split(':'))
            next_scheduled = (now + timedelta(days=1)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

        return {
            'enabled': self.config.enabled,
            'price_thresholds': self.config.price_thresholds,
            'scheduled_times': self.config.scheduled_times,
            'next_scheduled': next_scheduled.strftime('%Y-%m-%d %H:%M') if next_scheduled else None,
            'last_triggered': {
                k: v.strftime('%Y-%m-%d %H:%M:%S')
                for k, v in self._last_triggered.items()
            },
            'cooldown_hours': self.config.cooldown_hours,
            'generate_video': self.config.generate_video,
            'total_generated': len(self._generated_files),
        }

    def get_recent_files(self, limit: int = 5) -> List[Path]:
        """Get the most recently generated files."""
        return self._generated_files[-limit:][::-1]  # Most recent first

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable auto-triggers."""
        self.config.enabled = enabled

    def set_video_mode(self, generate_video: bool) -> None:
        """Set whether to generate video or image only."""
        self.config.generate_video = generate_video
