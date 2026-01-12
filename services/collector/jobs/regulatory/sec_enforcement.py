"""
SEC Enforcement Collector

Monitors SEC litigation releases, enforcement actions, and administrative proceedings.
Trust Tier: 1 (Official) - Creates Events

Sources:
- SEC Litigation Releases: https://www.sec.gov/litigation/litreleases.htm
- SEC Administrative Proceedings: https://www.sec.gov/litigation/admin.htm
- SEC AAER (Accounting): https://www.sec.gov/divisions/enforce/friactions.htm
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


# Action type patterns
ACTION_PATTERNS = {
    'wells_notice': [
        r'wells notice',
        r'wells letter',
        r'staff recommendation',
    ],
    'settlement': [
        r'settl(ed?|ement|ing)',
        r'agreed to pay',
        r'consent(ed)?',
        r'without admitting',
    ],
    'cease_desist': [
        r'cease[- ]and[- ]desist',
        r'stop order',
        r'trading suspension',
    ],
    'criminal_referral': [
        r'criminal',
        r'doj',
        r'department of justice',
        r'indictment',
        r'plea',
        r'guilty',
    ],
    'penalty': [
        r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion)?',
        r'civil (?:money )?penalty',
        r'disgorgement',
        r'fine[sd]?',
    ],
    'fraud': [
        r'fraud',
        r'scheme',
        r'manipulat',
        r'decei',
        r'misrepresent',
    ],
}

# Banks we monitor (by name patterns)
MONITORED_BANKS = [
    'jpmorgan', 'jp morgan', 'chase',
    'citigroup', 'citi', 'citibank',
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


class SECEnforcementCollector(BaseCollector):
    """
    Collects SEC enforcement actions and litigation releases.

    Creates Tier 1 Events for:
    - Litigation releases
    - Administrative proceedings
    - Accounting enforcement releases
    """

    source_name = "SEC Enforcement"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 60  # Check hourly

    # SEC URLs
    LITIGATION_URL = "https://www.sec.gov/litigation/litreleases.htm"
    ADMIN_URL = "https://www.sec.gov/litigation/admin.htm"
    AAER_URL = "https://www.sec.gov/divisions/enforce/friactions.htm"

    async def fetch(self) -> List[RawData]:
        """Fetch SEC enforcement pages"""
        raw_data = []

        urls = [
            (self.LITIGATION_URL, 'litigation'),
            (self.ADMIN_URL, 'admin'),
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
                print(f"[SEC Enforcement] Failed to fetch {url}: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse SEC enforcement releases into Events"""
        events = []
        page_type = raw.headers.get('page_type', 'unknown')

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # Find release entries (SEC uses various formats)
            entries = self._extract_entries(soup, page_type)

            for entry in entries:
                event = self._parse_entry(entry, page_type)
                if event:
                    events.append(event)

        except Exception as e:
            print(f"[SEC Enforcement] Parse error: {e}")

        return events

    def _extract_entries(self, soup: BeautifulSoup, page_type: str) -> List[Dict]:
        """Extract release entries from SEC page"""
        entries = []

        # SEC litigation releases format
        if page_type == 'litigation':
            # Look for table rows or list items
            for row in soup.select('table tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = row.find('a')
                    if link:
                        entries.append({
                            'title': link.get_text(strip=True),
                            'url': self._make_absolute_url(link.get('href', '')),
                            'date': self._extract_date(cells),
                            'description': cells[-1].get_text(strip=True) if cells else '',
                        })

            # Also check for newer list format
            for item in soup.select('.release-item, .list-item, li'):
                link = item.find('a')
                if link and 'litreleases' in str(link.get('href', '')):
                    entries.append({
                        'title': link.get_text(strip=True),
                        'url': self._make_absolute_url(link.get('href', '')),
                        'date': self._extract_date_from_text(item.get_text()),
                        'description': item.get_text(strip=True),
                    })

        # Admin proceedings format
        elif page_type == 'admin':
            for row in soup.select('table tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = row.find('a')
                    if link:
                        entries.append({
                            'title': link.get_text(strip=True),
                            'url': self._make_absolute_url(link.get('href', '')),
                            'date': self._extract_date(cells),
                            'description': cells[-1].get_text(strip=True) if cells else '',
                            'type': 'admin_proceeding',
                        })

        return entries[:50]  # Limit to most recent 50

    def _parse_entry(self, entry: Dict, page_type: str) -> Optional[Event]:
        """Parse a single entry into an Event"""
        title = entry.get('title', '')
        description = entry.get('description', '')
        full_text = f"{title} {description}".lower()

        # Check if this involves a monitored bank
        entity_match = None
        for bank in MONITORED_BANKS:
            if bank in full_text:
                entity_match = bank
                break

        # Determine action type
        action_type = self._determine_action_type(full_text)

        # Extract penalty amount if present
        penalty = self._extract_penalty(full_text)

        # Build event payload
        payload = {
            'title': title,
            'description': description,
            'url': entry.get('url', ''),
            'action_type': action_type,
            'page_type': page_type,
            'entity_mentioned': entity_match,
        }

        if penalty:
            payload['penalty_amount'] = penalty

        # Parse date
        published_at = None
        if entry.get('date'):
            try:
                published_at = datetime.strptime(entry['date'], '%Y-%m-%d')
            except:
                pass

        return Event(
            event_type='regulator_action',
            source_id=self.source_id,
            payload=payload,
            entity_id=None,  # Will be resolved by entity resolver
            published_at=published_at,
        )

    def _determine_action_type(self, text: str) -> str:
        """Determine the type of enforcement action"""
        for action_type, patterns in ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return action_type
        return 'enforcement'

    def _extract_penalty(self, text: str) -> Optional[float]:
        """Extract penalty amount from text"""
        # Pattern: $X million or $X,XXX,XXX
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d{1,3}(?:,\d{3})+(?:\.\d+)?)',
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

    def _extract_date(self, cells: List) -> Optional[str]:
        """Extract date from table cells"""
        for cell in cells:
            text = cell.get_text(strip=True)
            date = self._extract_date_from_text(text)
            if date:
                return date
        return None

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from text string"""
        # Try various date formats
        patterns = [
            (r'(\d{1,2}/\d{1,2}/\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2}/\d{1,2}/\d{2})', '%m/%d/%y'),
            (r'(\w+ \d{1,2}, \d{4})', '%B %d, %Y'),
            (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
        ]

        for pattern, fmt in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date = datetime.strptime(match.group(1), fmt)
                    return date.strftime('%Y-%m-%d')
                except:
                    continue

        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.sec.gov{url}"
        return f"https://www.sec.gov/{url}"


class SECWhistleblowerCollector(BaseCollector):
    """
    Collects SEC Whistleblower covered actions and awards.

    Trust Tier: 1 (Official) - Creates Events
    """

    source_name = "SEC Whistleblower"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 240  # Check every 4 hours

    WHISTLEBLOWER_URL = "https://www.sec.gov/whistleblower/pressreleases"

    async def fetch(self) -> List[RawData]:
        """Fetch SEC whistleblower press releases"""
        try:
            result = await self.fetcher.fetch(self.WHISTLEBLOWER_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            return [RawData(
                content=result.content,
                url=self.WHISTLEBLOWER_URL,
                fetched_at=result.fetched_at,
            )]
        except Exception as e:
            print(f"[SEC Whistleblower] Fetch error: {e}")
            return []

    def parse(self, raw: RawData) -> List[Event]:
        """Parse whistleblower releases into Events"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # Find press release entries
            for item in soup.select('.press-release, .views-row, article'):
                link = item.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                url = self._make_absolute_url(link.get('href', ''))

                # Extract award amount if mentioned
                award = self._extract_award(title)

                # Check for bank mentions
                entity_match = None
                title_lower = title.lower()
                for bank in MONITORED_BANKS:
                    if bank in title_lower:
                        entity_match = bank
                        break

                events.append(Event(
                    event_type='covered_action',
                    source_id=self.source_id,
                    payload={
                        'title': title,
                        'url': url,
                        'award_amount': award,
                        'entity_mentioned': entity_match,
                    },
                    entity_id=None,
                ))

        except Exception as e:
            print(f"[SEC Whistleblower] Parse error: {e}")

        return events[:20]

    def _extract_award(self, text: str) -> Optional[float]:
        """Extract award amount from text"""
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d{1,3}(?:,\d{3})+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                if 'million' in pattern:
                    return amount * 1_000_000
                return amount

        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.sec.gov{url}"
        return f"https://www.sec.gov/{url}"
