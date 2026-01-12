"""
Collector job runner using APScheduler.
Manages scheduling and execution of all data collectors.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Type
from dataclasses import dataclass, field

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from .jobs.base import BaseCollector, TrustTier
from .fetcher import Fetcher


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CollectorStats:
    """Statistics for a single collector run"""
    source_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    events_created: int = 0
    claims_created: int = 0
    duplicates_skipped: int = 0
    errors: int = 0
    success: bool = True


@dataclass
class RunnerStatus:
    """Overall status of the collector runner"""
    started_at: datetime
    is_running: bool
    collectors_registered: int
    collectors_healthy: int
    last_stats: Dict[str, CollectorStats] = field(default_factory=dict)


class CollectorRunner:
    """
    Manages scheduled execution of data collectors.

    Features:
    - Register collectors with custom schedules
    - APScheduler-based job management
    - Health monitoring and stats
    - Graceful shutdown
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        fetcher: Optional[Fetcher] = None,
    ):
        self.db_url = db_url
        self.fetcher = fetcher or Fetcher()

        # APScheduler
        self.scheduler = AsyncIOScheduler()

        # Registered collectors
        self._collectors: Dict[str, BaseCollector] = {}

        # Stats tracking
        self._stats: Dict[str, CollectorStats] = {}
        self._started_at: Optional[datetime] = None
        self._is_running = False

        # Event store (will be initialized with db connection)
        self._db = None

    async def initialize_db(self):
        """Initialize database connection"""
        if self.db_url:
            from db.event_store import EventStore
            self._db = EventStore(self.db_url)
            await self._db.connect()

    def register_collector(
        self,
        collector_class: Type[BaseCollector],
        frequency_minutes: Optional[int] = None,
        cron_expression: Optional[str] = None,
        enabled: bool = True,
    ):
        """
        Register a collector with the runner.

        Args:
            collector_class: Class inheriting from BaseCollector
            frequency_minutes: Run every N minutes (overrides collector default)
            cron_expression: Cron expression for scheduling (takes precedence)
            enabled: Whether collector is active
        """
        # Instantiate collector
        collector = collector_class(fetcher=self.fetcher, db=self._db)

        # Use provided frequency or collector default
        freq = frequency_minutes or collector.frequency_minutes

        collector_id = collector.source_name.lower().replace(' ', '_')
        self._collectors[collector_id] = collector

        if not enabled:
            logger.info(f"Collector {collector.source_name} registered but disabled")
            return

        # Create trigger
        if cron_expression:
            trigger = CronTrigger.from_crontab(cron_expression)
        else:
            trigger = IntervalTrigger(minutes=freq)

        # Add job to scheduler
        self.scheduler.add_job(
            self._run_collector,
            trigger=trigger,
            args=[collector_id],
            id=collector_id,
            name=f"Collector: {collector.source_name}",
            replace_existing=True,
        )

        logger.info(f"Registered collector: {collector.source_name} (every {freq} min)")

    async def _run_collector(self, collector_id: str):
        """Execute a single collector"""
        collector = self._collectors.get(collector_id)
        if not collector:
            logger.error(f"Unknown collector: {collector_id}")
            return

        stats = CollectorStats(
            source_name=collector.source_name,
            started_at=datetime.utcnow(),
        )

        try:
            logger.info(f"Running collector: {collector.source_name}")
            results = await collector.collect()

            stats.events_created = results.get('events_created', 0)
            stats.claims_created = results.get('claims_created', 0)
            stats.duplicates_skipped = results.get('duplicates_skipped', 0)
            stats.errors = results.get('errors', 0)
            stats.success = stats.errors == 0

            logger.info(
                f"Collector {collector.source_name}: "
                f"{stats.events_created} events, "
                f"{stats.claims_created} claims, "
                f"{stats.duplicates_skipped} duplicates, "
                f"{stats.errors} errors"
            )

        except Exception as e:
            stats.success = False
            stats.errors = 1
            logger.error(f"Collector {collector.source_name} failed: {e}")

        stats.completed_at = datetime.utcnow()
        self._stats[collector_id] = stats

    async def run_all_now(self) -> Dict[str, CollectorStats]:
        """Run all collectors immediately (for testing or manual refresh)"""
        tasks = [
            self._run_collector(collector_id)
            for collector_id in self._collectors
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self._stats.copy()

    async def run_by_tier(self, tier: TrustTier) -> Dict[str, CollectorStats]:
        """Run only collectors of a specific trust tier"""
        tasks = [
            self._run_collector(collector_id)
            for collector_id, collector in self._collectors.items()
            if collector.trust_tier == tier
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        return {
            k: v for k, v in self._stats.items()
            if self._collectors[k].trust_tier == tier
        }

    def start(self):
        """Start the scheduler"""
        if self._is_running:
            logger.warning("Runner already started")
            return

        self.scheduler.start()
        self._is_running = True
        self._started_at = datetime.utcnow()
        logger.info(f"Collector runner started with {len(self._collectors)} collectors")

    async def stop(self):
        """Stop the scheduler gracefully"""
        if not self._is_running:
            return

        self.scheduler.shutdown(wait=True)
        await self.fetcher.close()

        if self._db:
            await self._db.close()

        self._is_running = False
        logger.info("Collector runner stopped")

    def get_status(self) -> RunnerStatus:
        """Get current runner status"""
        healthy = sum(
            1 for c in self._collectors.values()
            if c.get_status()['healthy']
        )

        return RunnerStatus(
            started_at=self._started_at or datetime.utcnow(),
            is_running=self._is_running,
            collectors_registered=len(self._collectors),
            collectors_healthy=healthy,
            last_stats=self._stats.copy(),
        )

    def get_collector_status(self, collector_id: str) -> Optional[Dict]:
        """Get status of a specific collector"""
        collector = self._collectors.get(collector_id)
        if not collector:
            return None

        status = collector.get_status()
        if collector_id in self._stats:
            stats = self._stats[collector_id]
            status['last_run_stats'] = {
                'events_created': stats.events_created,
                'claims_created': stats.claims_created,
                'duplicates_skipped': stats.duplicates_skipped,
                'errors': stats.errors,
                'success': stats.success,
            }

        return status


# Default runner instance
runner: Optional[CollectorRunner] = None


def get_runner() -> CollectorRunner:
    """Get or create the default runner instance"""
    global runner
    if runner is None:
        runner = CollectorRunner()
    return runner


async def setup_default_collectors():
    """Register all default collectors with the runner"""
    r = get_runner()

    # Import regulatory collectors (Tier 1 - Official)
    from .jobs.regulatory import REGULATORY_COLLECTORS

    # Import liquidity collectors (Tier 1 - Official)
    from .jobs.liquidity import LIQUIDITY_COLLECTORS

    # Register all regulatory collectors
    for collector_class, frequency in REGULATORY_COLLECTORS:
        r.register_collector(collector_class, frequency_minutes=frequency)

    # Register liquidity collectors
    for collector_class, frequency in LIQUIDITY_COLLECTORS:
        r.register_collector(collector_class, frequency_minutes=frequency)

    total = len(REGULATORY_COLLECTORS) + len(LIQUIDITY_COLLECTORS)
    logger.info(f"Registered {total} collectors ({len(REGULATORY_COLLECTORS)} regulatory, {len(LIQUIDITY_COLLECTORS)} liquidity)")
