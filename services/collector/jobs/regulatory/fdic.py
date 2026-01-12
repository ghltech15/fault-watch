"""
FDIC Bank Failures Collector

Monitors FDIC bank failure announcements and resolutions.
Trust Tier: 1 (Official) - Creates Events

Sources:
- FDIC Failed Banks List: https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/
- FDIC Press Releases: https://www.fdic.gov/news/press-releases/
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


class FDICBankFailuresCollector(BaseCollector):
    """
    Collects FDIC bank failure announcements.

    Critical events for systemic risk monitoring:
    - Bank failures
    - FDIC receiverships
    - Assisted transactions
    - Bank closings
    """

    source_name = "FDIC Bank Failures"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 240  # Check every 4 hours

    FAILURES_URL = "https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/"
    PRESS_URL = "https://www.fdic.gov/news/press-releases/"

    async def fetch(self) -> List[RawData]:
        """Fetch FDIC pages"""
        raw_data = []

        urls = [
            (self.FAILURES_URL, 'failures'),
            (self.PRESS_URL, 'press'),
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
                print(f"[FDIC] Failed to fetch {url}: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse FDIC data into Events"""
        page_type = raw.headers.get('page_type', 'unknown')

        if page_type == 'failures':
            return self._parse_failures(raw)
        elif page_type == 'press':
            return self._parse_press(raw)

        return []

    def _parse_failures(self, raw: RawData) -> List[Event]:
        """Parse failed banks list"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # FDIC failed banks table
            for row in soup.select('table tr'):
                cells = row.find_all('td')
                if len(cells) >= 5:
                    event = self._parse_failure_row(cells)
                    if event:
                        events.append(event)

        except Exception as e:
            print(f"[FDIC] Parse failures error: {e}")

        return events[:50]

    def _parse_failure_row(self, cells: List) -> Optional[Event]:
        """Parse a single failure row"""
        try:
            bank_name = cells[0].get_text(strip=True)
            city = cells[1].get_text(strip=True) if len(cells) > 1 else ''
            state = cells[2].get_text(strip=True) if len(cells) > 2 else ''
            cert = cells[3].get_text(strip=True) if len(cells) > 3 else ''
            acquiring = cells[4].get_text(strip=True) if len(cells) > 4 else ''
            closing_date = cells[5].get_text(strip=True) if len(cells) > 5 else ''

            if not bank_name or bank_name.lower() == 'bank name':
                return None

            # Parse closing date
            published_at = self._parse_date(closing_date)

            return Event(
                event_type='bank_failure',
                source_id=self.source_id,
                payload={
                    'bank_name': bank_name,
                    'city': city,
                    'state': state,
                    'cert_number': cert,
                    'acquiring_institution': acquiring,
                    'closing_date': closing_date,
                    'regulator': 'FDIC',
                },
                entity_id=None,
                published_at=published_at,
            )

        except Exception as e:
            print(f"[FDIC] Row parse error: {e}")
            return None

    def _parse_press(self, raw: RawData) -> List[Event]:
        """Parse FDIC press releases"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # Look for bank failure related press releases
            keywords = ['fail', 'close', 'receivership', 'resolution', 'systemic']

            for item in soup.select('.views-row, article, .press-release'):
                link = item.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                title_lower = title.lower()

                # Only process bank failure related
                if not any(kw in title_lower for kw in keywords):
                    continue

                url = self._make_absolute_url(link.get('href', ''))

                # Extract date
                date_elem = item.find(class_=re.compile(r'date|time'))
                published_at = None
                if date_elem:
                    published_at = self._parse_date(date_elem.get_text(strip=True))

                events.append(Event(
                    event_type='bank_failure',
                    source_id=self.source_id,
                    payload={
                        'title': title,
                        'url': url,
                        'type': 'press_release',
                        'regulator': 'FDIC',
                    },
                    entity_id=None,
                    published_at=published_at,
                ))

        except Exception as e:
            print(f"[FDIC] Press parse error: {e}")

        return events[:20]

    def _parse_date(self, text: str) -> Optional[datetime]:
        """Parse date from text"""
        if not text:
            return None

        patterns = [
            ('%B %d, %Y', r'(\w+ \d{1,2}, \d{4})'),
            ('%m/%d/%Y', r'(\d{1,2}/\d{1,2}/\d{4})'),
            ('%m-%d-%Y', r'(\d{1,2}-\d{1,2}-\d{4})'),
            ('%Y-%m-%d', r'(\d{4}-\d{2}-\d{2})'),
        ]

        for fmt, pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return datetime.strptime(match.group(1), fmt)
                except:
                    continue

        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.fdic.gov{url}"
        return f"https://www.fdic.gov/{url}"


class FDICEnforcementCollector(BaseCollector):
    """
    Collects FDIC enforcement actions.

    Actions include:
    - Cease and Desist Orders
    - Civil Money Penalties
    - Removal/Prohibition Orders
    - Written Agreements
    """

    source_name = "FDIC Enforcement"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 240

    ENFORCEMENT_URL = "https://www.fdic.gov/resources/supervision-and-examinations/enforcement/index.html"

    async def fetch(self) -> List[RawData]:
        """Fetch FDIC enforcement page"""
        try:
            result = await self.fetcher.fetch(self.ENFORCEMENT_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            return [RawData(
                content=result.content,
                url=self.ENFORCEMENT_URL,
                fetched_at=result.fetched_at,
            )]
        except Exception as e:
            print(f"[FDIC Enforcement] Fetch error: {e}")
            return []

    def parse(self, raw: RawData) -> List[Event]:
        """Parse FDIC enforcement actions"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            for row in soup.select('table tr, .views-row, article'):
                link = row.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                url = self._make_absolute_url(link.get('href', ''))
                title_lower = title.lower()

                # Determine action type
                action_type = 'enforcement'
                if 'cease' in title_lower and 'desist' in title_lower:
                    action_type = 'cease_desist'
                elif 'penalty' in title_lower or 'cmp' in title_lower:
                    action_type = 'civil_money_penalty'
                elif 'removal' in title_lower or 'prohibition' in title_lower:
                    action_type = 'removal'
                elif 'agreement' in title_lower:
                    action_type = 'formal_agreement'

                events.append(Event(
                    event_type='regulator_action',
                    source_id=self.source_id,
                    payload={
                        'title': title,
                        'url': url,
                        'action_type': action_type,
                        'regulator': 'FDIC',
                    },
                    entity_id=None,
                ))

        except Exception as e:
            print(f"[FDIC Enforcement] Parse error: {e}")

        return events[:30]

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.fdic.gov{url}"
        return f"https://www.fdic.gov/{url}"
