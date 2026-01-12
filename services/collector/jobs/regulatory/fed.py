"""
Federal Reserve Collector

Monitors Fed data releases including H.4.1 balance sheet.
Trust Tier: 1 (Official) - Creates Events

Sources:
- Fed H.4.1: https://www.federalreserve.gov/releases/h41/
- Fed Press Releases: https://www.federalreserve.gov/newsevents/pressreleases.htm
- FOMC Statements: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


class FedH41Collector(BaseCollector):
    """
    Collects Federal Reserve H.4.1 balance sheet data.

    Monitors:
    - Total assets
    - Emergency lending facilities
    - Discount window usage
    - Repo operations
    - QE holdings
    """

    source_name = "Fed H.4.1"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 60  # Check hourly (released weekly on Thursday)

    H41_URL = "https://www.federalreserve.gov/releases/h41/current/"
    H41_XML_URL = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H41&series=3d9b8eb3b7e6503a7db66c7a2df8afca&lastobs=10&from=&to=&filetype=csv&label=include&layout=seriescolumn"

    async def fetch(self) -> List[RawData]:
        """Fetch H.4.1 data"""
        raw_data = []

        try:
            # Try HTML page first
            result = await self.fetcher.fetch(self.H41_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            raw_data.append(RawData(
                content=result.content,
                url=self.H41_URL,
                fetched_at=result.fetched_at,
                headers={'format': 'html'},
            ))
        except Exception as e:
            print(f"[Fed H.4.1] HTML fetch error: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse H.4.1 data into Events"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # Extract key balance sheet figures
            h41_data = self._extract_h41_data(soup)

            if h41_data:
                events.append(Event(
                    event_type='fed_balance_sheet',
                    source_id=self.source_id,
                    payload=h41_data,
                    entity_id=None,
                    published_at=h41_data.get('release_date'),
                ))

                # Check for emergency facility usage
                if h41_data.get('emergency_lending', 0) > 0:
                    events.append(Event(
                        event_type='fed_facility_usage',
                        source_id=self.source_id,
                        payload={
                            'facility_type': 'emergency',
                            'amount': h41_data['emergency_lending'],
                            'release_date': h41_data.get('release_date'),
                        },
                        entity_id=None,
                    ))

        except Exception as e:
            print(f"[Fed H.4.1] Parse error: {e}")

        return events

    def _extract_h41_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract H.4.1 balance sheet data"""
        data = {
            'release_date': datetime.utcnow(),
        }

        # Try to find the release date
        date_elem = soup.find(class_=re.compile(r'release-date|date'))
        if date_elem:
            date = self._parse_date(date_elem.get_text(strip=True))
            if date:
                data['release_date'] = date

        # H.4.1 has various table formats - try to extract key figures
        tables = soup.find_all('table')

        for table in tables:
            text = table.get_text().lower()

            # Total assets
            if 'total assets' in text:
                value = self._extract_billions(table.get_text())
                if value:
                    data['total_assets'] = value

            # Emergency facilities
            if 'credit extension' in text or 'liquidity facility' in text:
                value = self._extract_billions(table.get_text())
                if value:
                    data['emergency_lending'] = value

            # Discount window
            if 'discount window' in text or 'primary credit' in text:
                value = self._extract_billions(table.get_text())
                if value:
                    data['discount_window'] = value

            # Treasury holdings
            if 'treasury securities' in text:
                value = self._extract_billions(table.get_text())
                if value:
                    data['treasury_holdings'] = value

            # MBS holdings
            if 'mortgage-backed' in text:
                value = self._extract_billions(table.get_text())
                if value:
                    data['mbs_holdings'] = value

        return data if len(data) > 1 else None

    def _extract_billions(self, text: str) -> Optional[float]:
        """Extract dollar amount in billions"""
        # Pattern for billions/millions
        patterns = [
            r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s*(?:billion|B)',
            r'\$(\d{1,3}(?:,\d{3})+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*trillion',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(',', ''))
                if 'trillion' in pattern.lower():
                    return value * 1000  # Convert to billions
                return value

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


class FedPressCollector(BaseCollector):
    """
    Collects Federal Reserve press releases.

    Monitors:
    - FOMC statements
    - Emergency announcements
    - Supervisory actions
    """

    source_name = "Fed Press"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 30  # Check every 30 minutes (FOMC days are critical)

    PRESS_URL = "https://www.federalreserve.gov/newsevents/pressreleases.htm"

    # Keywords for relevant press releases
    KEYWORDS = [
        'discount window',
        'lending facility',
        'liquidity',
        'emergency',
        'stress',
        'bank',
        'silver',
        'gold',
        'precious metal',
        'enforcement',
        'supervisory',
    ]

    async def fetch(self) -> List[RawData]:
        """Fetch Fed press releases"""
        try:
            result = await self.fetcher.fetch(self.PRESS_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            return [RawData(
                content=result.content,
                url=self.PRESS_URL,
                fetched_at=result.fetched_at,
            )]
        except Exception as e:
            print(f"[Fed Press] Fetch error: {e}")
            return []

    def parse(self, raw: RawData) -> List[Event]:
        """Parse Fed press releases"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            for item in soup.select('.row--press-release, .newsitem, article'):
                link = item.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                url = self._make_absolute_url(link.get('href', ''))

                # Check relevance
                title_lower = title.lower()
                if not any(kw in title_lower for kw in self.KEYWORDS):
                    continue

                # Extract date
                date_elem = item.find(class_=re.compile(r'date|time'))
                published_at = None
                if date_elem:
                    published_at = self._parse_date(date_elem.get_text(strip=True))

                # Determine type
                event_type = 'fed_announcement'
                if 'fomc' in title_lower or 'rate' in title_lower:
                    event_type = 'fed_rate_decision'
                elif 'enforcement' in title_lower or 'supervisory' in title_lower:
                    event_type = 'regulator_action'
                elif 'facility' in title_lower or 'lending' in title_lower:
                    event_type = 'fed_facility_usage'

                events.append(Event(
                    event_type=event_type,
                    source_id=self.source_id,
                    payload={
                        'title': title,
                        'url': url,
                        'regulator': 'Fed',
                    },
                    entity_id=None,
                    published_at=published_at,
                ))

        except Exception as e:
            print(f"[Fed Press] Parse error: {e}")

        return events[:20]

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
            return f"https://www.federalreserve.gov{url}"
        return f"https://www.federalreserve.gov/{url}"
