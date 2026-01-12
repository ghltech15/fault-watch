"""
CFTC Enforcement Collector

Monitors CFTC press releases, enforcement actions, and COT reports.
Trust Tier: 1 (Official) - Creates Events

Sources:
- CFTC Press Releases: https://www.cftc.gov/PressRoom/PressReleases
- CFTC Enforcement: https://www.cftc.gov/LawRegulation/Enforcement
- COT Reports: https://www.cftc.gov/MarketReports/CommitmentsofTraders
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


# Keywords for precious metals related actions
PM_KEYWORDS = [
    'silver', 'gold', 'precious metal', 'comex', 'futures',
    'manipulation', 'spoofing', 'position limit', 'delivery',
]

# Monitored banks
MONITORED_BANKS = [
    'jpmorgan', 'jp morgan', 'chase',
    'citigroup', 'citi',
    'bank of america', 'bofa',
    'morgan stanley',
    'goldman sachs', 'goldman',
    'wells fargo',
    'ubs',
    'credit suisse',
    'hsbc',
    'barclays',
    'deutsche bank',
]


class CFTCEnforcementCollector(BaseCollector):
    """
    Collects CFTC enforcement actions and press releases.

    Focuses on:
    - Precious metals manipulation
    - Spoofing cases
    - Position limit violations
    - Delivery failures
    """

    source_name = "CFTC Enforcement"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 120  # Check every 2 hours

    PRESS_URL = "https://www.cftc.gov/PressRoom/PressReleases"
    ENFORCEMENT_URL = "https://www.cftc.gov/LawRegulation/Enforcement"

    async def fetch(self) -> List[RawData]:
        """Fetch CFTC pages"""
        raw_data = []

        urls = [
            (self.PRESS_URL, 'press'),
            (self.ENFORCEMENT_URL, 'enforcement'),
        ]

        for url, page_type in urls:
            try:
                result = await self.fetcher.fetch(url, headers={
                    'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
                })
                raw_data.append(RawData(
                    content=result.content,
                    url=url,
                    fetched_at=result.fetched_at,
                    headers={'page_type': page_type},
                ))
            except Exception as e:
                print(f"[CFTC] Failed to fetch {url}: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse CFTC releases into Events"""
        events = []
        page_type = raw.headers.get('page_type', 'unknown')

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # Find press release entries
            for item in soup.select('.views-row, .press-release-row, article, tr'):
                event = self._parse_item(item, page_type)
                if event:
                    events.append(event)

        except Exception as e:
            print(f"[CFTC] Parse error: {e}")

        return events[:30]

    def _parse_item(self, item, page_type: str) -> Optional[Event]:
        """Parse a single item into an Event"""
        link = item.find('a')
        if not link:
            return None

        title = link.get_text(strip=True)
        url = self._make_absolute_url(link.get('href', ''))

        # Skip if no title
        if not title or len(title) < 10:
            return None

        title_lower = title.lower()

        # Check relevance (precious metals or monitored banks)
        is_relevant = False
        entity_match = None

        for keyword in PM_KEYWORDS:
            if keyword in title_lower:
                is_relevant = True
                break

        for bank in MONITORED_BANKS:
            if bank in title_lower:
                is_relevant = True
                entity_match = bank
                break

        # Only create events for relevant items
        if not is_relevant:
            return None

        # Determine action type
        action_type = self._determine_action_type(title_lower)

        # Extract penalty if present
        penalty = self._extract_penalty(title)

        # Extract date
        date_elem = item.find(class_=re.compile(r'date|time'))
        published_at = None
        if date_elem:
            published_at = self._parse_date(date_elem.get_text(strip=True))

        return Event(
            event_type='regulator_action',
            source_id=self.source_id,
            payload={
                'title': title,
                'url': url,
                'action_type': action_type,
                'regulator': 'CFTC',
                'entity_mentioned': entity_match,
                'penalty_amount': penalty,
                'keywords_matched': [k for k in PM_KEYWORDS if k in title_lower],
            },
            entity_id=None,
            published_at=published_at,
        )

    def _determine_action_type(self, text: str) -> str:
        """Determine CFTC action type"""
        if 'spoof' in text:
            return 'spoofing'
        elif 'manipulat' in text:
            return 'manipulation'
        elif 'settlement' in text or 'settles' in text:
            return 'settlement'
        elif 'order' in text and ('civil' in text or 'penalty' in text):
            return 'penalty'
        elif 'charges' in text:
            return 'charges'
        elif 'position limit' in text:
            return 'position_limit_violation'
        return 'enforcement'

    def _extract_penalty(self, text: str) -> Optional[float]:
        """Extract penalty amount"""
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d{1,3}(?:,\d{3})+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                if 'billion' in pattern:
                    return amount * 1_000_000_000
                elif 'million' in pattern:
                    return amount * 1_000_000
                return amount

        return None

    def _parse_date(self, text: str) -> Optional[datetime]:
        """Parse date from text"""
        patterns = [
            '%B %d, %Y',
            '%m/%d/%Y',
            '%Y-%m-%d',
        ]

        for pattern in patterns:
            try:
                return datetime.strptime(text.strip(), pattern)
            except:
                continue

        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.cftc.gov{url}"
        return f"https://www.cftc.gov/{url}"


class CFTCCOTCollector(BaseCollector):
    """
    Collects CFTC Commitments of Traders (COT) reports.

    Tracks silver futures positioning by:
    - Commercial traders (banks, hedgers)
    - Non-commercial traders (speculators)
    - Open interest changes
    """

    source_name = "CFTC COT"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 1440  # Check daily (reports released weekly on Tuesday)

    # COT reports in CSV format
    COT_URL = "https://www.cftc.gov/dea/newcot/deafut.txt"

    # Silver contract code
    SILVER_CODE = "084691"

    async def fetch(self) -> List[RawData]:
        """Fetch COT report data"""
        try:
            result = await self.fetcher.fetch(self.COT_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            return [RawData(
                content=result.content,
                url=self.COT_URL,
                fetched_at=result.fetched_at,
            )]
        except Exception as e:
            print(f"[CFTC COT] Fetch error: {e}")
            return []

    def parse(self, raw: RawData) -> List[Event]:
        """Parse COT report into Events"""
        events = []

        try:
            content = raw.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Parse the fixed-width format COT report
            lines = content.strip().split('\n')

            for line in lines:
                # Skip header lines
                if not line.strip() or 'CFTC' in line or 'Market' in line:
                    continue

                # Look for silver
                if 'SILVER' in line.upper() or self.SILVER_CODE in line:
                    cot_data = self._parse_cot_line(line)
                    if cot_data:
                        events.append(Event(
                            event_type='cot_report',
                            source_id=self.source_id,
                            payload=cot_data,
                            entity_id=None,
                            published_at=cot_data.get('report_date'),
                        ))

        except Exception as e:
            print(f"[CFTC COT] Parse error: {e}")

        return events

    def _parse_cot_line(self, line: str) -> Optional[Dict]:
        """Parse a single COT report line"""
        # COT format is complex fixed-width
        # This is a simplified parser - full implementation would handle all columns

        try:
            parts = line.split()
            if len(parts) < 10:
                return None

            return {
                'metal': 'silver',
                'report_date': datetime.utcnow(),  # Would parse from report
                'commercial_long': self._safe_int(parts, 3),
                'commercial_short': self._safe_int(parts, 4),
                'non_commercial_long': self._safe_int(parts, 5),
                'non_commercial_short': self._safe_int(parts, 6),
                'total_open_interest': self._safe_int(parts, 7),
                'commercial_net': None,  # Calculated
                'non_commercial_net': None,  # Calculated
            }
        except Exception:
            return None

    def _safe_int(self, parts: List[str], idx: int) -> Optional[int]:
        """Safely extract integer from parts"""
        try:
            if idx < len(parts):
                return int(parts[idx].replace(',', ''))
        except:
            pass
        return None
