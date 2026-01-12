"""
OCC (Office of the Comptroller of the Currency) Enforcement Collector

Monitors OCC enforcement actions against national banks.
Trust Tier: 1 (Official) - Creates Events

Sources:
- OCC Enforcement Actions: https://www.occ.gov/topics/laws-and-regulations/enforcement-actions/
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


# Action types for OCC
OCC_ACTION_TYPES = {
    'cease_desist': ['cease and desist', 'c&d', 'cease-and-desist'],
    'consent_order': ['consent order', 'written agreement'],
    'civil_money_penalty': ['civil money penalty', 'cmp', 'fine'],
    'removal': ['removal', 'prohibition', 'barred'],
    'formal_agreement': ['formal agreement'],
    'prompt_corrective_action': ['prompt corrective action', 'pca'],
    'safety_soundness': ['safety and soundness', 'unsafe practice'],
}

# Major banks under OCC supervision
OCC_SUPERVISED_BANKS = [
    'jpmorgan chase',
    'bank of america',
    'wells fargo',
    'citibank',
    'u.s. bank',
    'pnc bank',
    'truist',
    'capital one',
    'td bank',
    'goldman sachs bank',
]


class OCCEnforcementCollector(BaseCollector):
    """
    Collects OCC enforcement actions.

    The OCC supervises national banks and federal savings associations.
    Actions include:
    - Cease and Desist Orders
    - Civil Money Penalties
    - Consent Orders
    - Formal Agreements
    - Removal/Prohibition Orders
    """

    source_name = "OCC Enforcement"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 120  # Check every 2 hours

    BASE_URL = "https://www.occ.gov"
    ENFORCEMENT_URL = "https://www.occ.gov/topics/laws-and-regulations/enforcement-actions/index-enforcement-actions.html"

    async def fetch(self) -> List[RawData]:
        """Fetch OCC enforcement actions page"""
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
            print(f"[OCC] Fetch error: {e}")
            return []

    def parse(self, raw: RawData) -> List[Event]:
        """Parse OCC enforcement page into Events"""
        events = []

        try:
            soup = BeautifulSoup(raw.content, 'lxml')

            # OCC lists enforcement actions in tables or lists
            # Try multiple selectors
            entries = []

            # Table format
            for row in soup.select('table tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = row.find('a')
                    if link:
                        entries.append({
                            'title': link.get_text(strip=True),
                            'url': self._make_absolute_url(link.get('href', '')),
                            'cells': [c.get_text(strip=True) for c in cells],
                        })

            # List format
            for item in soup.select('.enforcement-action, .views-row, article'):
                link = item.find('a')
                if link:
                    entries.append({
                        'title': link.get_text(strip=True),
                        'url': self._make_absolute_url(link.get('href', '')),
                        'text': item.get_text(strip=True),
                    })

            # Parse each entry
            for entry in entries[:50]:
                event = self._parse_entry(entry)
                if event:
                    events.append(event)

        except Exception as e:
            print(f"[OCC] Parse error: {e}")

        return events

    def _parse_entry(self, entry: Dict) -> Optional[Event]:
        """Parse a single entry into an Event"""
        title = entry.get('title', '')
        if not title or len(title) < 5:
            return None

        full_text = f"{title} {entry.get('text', '')}".lower()

        # Check if this involves a monitored bank
        entity_match = None
        for bank in OCC_SUPERVISED_BANKS:
            if bank in full_text:
                entity_match = bank
                break

        # Determine action type
        action_type = self._determine_action_type(full_text)

        # Extract date from cells if available
        published_at = None
        cells = entry.get('cells', [])
        for cell in cells:
            date = self._parse_date(cell)
            if date:
                published_at = date
                break

        # Extract penalty amount if mentioned
        penalty = self._extract_penalty(full_text)

        return Event(
            event_type='regulator_action',
            source_id=self.source_id,
            payload={
                'title': title,
                'url': entry.get('url', ''),
                'action_type': action_type,
                'regulator': 'OCC',
                'entity_mentioned': entity_match,
                'penalty_amount': penalty,
            },
            entity_id=None,
            published_at=published_at,
        )

    def _determine_action_type(self, text: str) -> str:
        """Determine OCC action type"""
        for action_type, patterns in OCC_ACTION_TYPES.items():
            for pattern in patterns:
                if pattern in text:
                    return action_type
        return 'enforcement'

    def _extract_penalty(self, text: str) -> Optional[float]:
        """Extract penalty amount from text"""
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
            ('%B %d, %Y', r'(\w+ \d{1,2}, \d{4})'),
            ('%m/%d/%Y', r'(\d{1,2}/\d{1,2}/\d{4})'),
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
            return f"{self.BASE_URL}{url}"
        return f"{self.BASE_URL}/{url}"
