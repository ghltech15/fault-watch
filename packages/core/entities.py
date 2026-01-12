"""
Entity Resolution Utilities

Resolves entity references from various identifiers:
- SEC CIK numbers
- LEI (Legal Entity Identifier)
- Stock ticker symbols
- Company names and aliases
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID
import re


class EntityType(Enum):
    """Types of entities tracked"""
    BANK = 'bank'
    REGULATOR = 'regulator'
    METAL = 'metal'
    TICKER = 'ticker'
    PERSON = 'person'
    EXCHANGE = 'exchange'
    ETF = 'etf'


@dataclass
class Entity:
    """Represents a tracked entity (bank, metal, regulator, etc.)"""
    id: UUID
    entity_type: EntityType
    name: str
    aliases: List[str] = field(default_factory=list)
    cik: Optional[str] = None          # SEC Central Index Key
    lei: Optional[str] = None          # Legal Entity Identifier
    tickers: List[str] = field(default_factory=list)
    domain: Optional[str] = None       # Company website
    country: Optional[str] = None
    sector: Optional[str] = None

    def matches(self, query: str) -> bool:
        """Check if entity matches a query string"""
        query_lower = query.lower()

        # Exact CIK match
        if self.cik and query.strip('0') == self.cik.strip('0'):
            return True

        # Exact ticker match
        if query.upper() in [t.upper() for t in self.tickers]:
            return True

        # Name/alias match (case-insensitive)
        if query_lower == self.name.lower():
            return True
        if query_lower in [a.lower() for a in self.aliases]:
            return True

        # Partial name match (for longer queries)
        if len(query) >= 4 and query_lower in self.name.lower():
            return True

        return False


# Pre-built entity data (banks with silver/PM exposure)
KNOWN_ENTITIES: Dict[str, Dict] = {
    # Major US banks
    'JPM': {
        'name': 'JPMorgan Chase & Co.',
        'aliases': ['JPM', 'JPMorgan', 'JP Morgan', 'Chase'],
        'cik': '0000019617',
        'tickers': ['JPM'],
        'type': EntityType.BANK,
    },
    'C': {
        'name': 'Citigroup Inc.',
        'aliases': ['Citi', 'Citibank', 'Citigroup'],
        'cik': '0000831001',
        'tickers': ['C'],
        'type': EntityType.BANK,
    },
    'BAC': {
        'name': 'Bank of America Corporation',
        'aliases': ['BofA', 'BoA', 'Bank of America'],
        'cik': '0000070858',
        'tickers': ['BAC'],
        'type': EntityType.BANK,
    },
    'MS': {
        'name': 'Morgan Stanley',
        'aliases': ['MS'],
        'cik': '0000895421',
        'tickers': ['MS'],
        'type': EntityType.BANK,
    },
    'GS': {
        'name': 'Goldman Sachs Group Inc.',
        'aliases': ['Goldman', 'GS', 'Goldman Sachs'],
        'cik': '0000886982',
        'tickers': ['GS'],
        'type': EntityType.BANK,
    },
    'WFC': {
        'name': 'Wells Fargo & Company',
        'aliases': ['Wells', 'Wells Fargo'],
        'cik': '0000072971',
        'tickers': ['WFC'],
        'type': EntityType.BANK,
    },
    'UBS': {
        'name': 'UBS Group AG',
        'aliases': ['UBS'],
        'cik': '0001610520',
        'tickers': ['UBS'],
        'type': EntityType.BANK,
    },
    'CS': {
        'name': 'Credit Suisse Group AG',
        'aliases': ['CS', 'Credit Suisse'],
        'cik': '0001159510',
        'tickers': ['CS'],
        'type': EntityType.BANK,
    },
    'HSBC': {
        'name': 'HSBC Holdings plc',
        'aliases': ['HSBC'],
        'cik': '0001089113',
        'tickers': ['HSBC'],
        'type': EntityType.BANK,
    },
    'BCS': {
        'name': 'Barclays PLC',
        'aliases': ['Barclays'],
        'cik': '0000312069',
        'tickers': ['BCS'],
        'type': EntityType.BANK,
    },
    # Metals
    'SILVER': {
        'name': 'Silver',
        'aliases': ['Ag', 'XAG', 'silver'],
        'tickers': ['SI=F', 'SLV'],
        'type': EntityType.METAL,
    },
    'GOLD': {
        'name': 'Gold',
        'aliases': ['Au', 'XAU', 'gold'],
        'tickers': ['GC=F', 'GLD'],
        'type': EntityType.METAL,
    },
    # Regulators
    'SEC': {
        'name': 'Securities and Exchange Commission',
        'aliases': ['SEC'],
        'type': EntityType.REGULATOR,
    },
    'CFTC': {
        'name': 'Commodity Futures Trading Commission',
        'aliases': ['CFTC'],
        'type': EntityType.REGULATOR,
    },
    'OCC': {
        'name': 'Office of the Comptroller of the Currency',
        'aliases': ['OCC'],
        'type': EntityType.REGULATOR,
    },
    'FDIC': {
        'name': 'Federal Deposit Insurance Corporation',
        'aliases': ['FDIC'],
        'type': EntityType.REGULATOR,
    },
    'FED': {
        'name': 'Federal Reserve System',
        'aliases': ['Fed', 'Federal Reserve', 'The Fed'],
        'type': EntityType.REGULATOR,
    },
    # Exchanges
    'COMEX': {
        'name': 'COMEX',
        'aliases': ['CME COMEX', 'Comex'],
        'type': EntityType.EXCHANGE,
    },
    'LBMA': {
        'name': 'London Bullion Market Association',
        'aliases': ['LBMA'],
        'type': EntityType.EXCHANGE,
    },
}

# CIK to ticker mapping for fast lookup
CIK_MAP: Dict[str, str] = {
    data['cik']: key
    for key, data in KNOWN_ENTITIES.items()
    if 'cik' in data
}


class EntityResolver:
    """
    Resolves entity references from text or identifiers.

    Supports:
    - CIK number resolution
    - Ticker symbol resolution
    - Name/alias matching
    - Entity extraction from free text
    """

    def __init__(self, db=None):
        """
        Initialize resolver.

        Args:
            db: Optional database connection for dynamic resolution
        """
        self.db = db
        self._cache: Dict[str, Optional[Entity]] = {}

    def resolve(self, identifier: str) -> Optional[Entity]:
        """
        Resolve an identifier to an Entity.

        Args:
            identifier: CIK, ticker, name, or alias

        Returns:
            Entity if found, None otherwise
        """
        if identifier in self._cache:
            return self._cache[identifier]

        # Normalize
        identifier = identifier.strip()

        # Try CIK first
        if identifier.isdigit() or identifier.startswith('000'):
            cik = identifier.zfill(10)  # Pad to 10 digits
            if cik in CIK_MAP:
                entity = self._build_entity(CIK_MAP[cik])
                self._cache[identifier] = entity
                return entity

        # Try ticker
        upper = identifier.upper()
        if upper in KNOWN_ENTITIES:
            entity = self._build_entity(upper)
            self._cache[identifier] = entity
            return entity

        # Try name/alias search
        for key, data in KNOWN_ENTITIES.items():
            if identifier.lower() == data['name'].lower():
                entity = self._build_entity(key)
                self._cache[identifier] = entity
                return entity
            if 'aliases' in data:
                for alias in data['aliases']:
                    if identifier.lower() == alias.lower():
                        entity = self._build_entity(key)
                        self._cache[identifier] = entity
                        return entity

        # Not found
        self._cache[identifier] = None
        return None

    def _build_entity(self, key: str) -> Entity:
        """Build Entity from known data"""
        data = KNOWN_ENTITIES[key]
        return Entity(
            id=None,  # Will be populated from DB if available
            entity_type=data.get('type', EntityType.TICKER),
            name=data['name'],
            aliases=data.get('aliases', []),
            cik=data.get('cik'),
            lei=data.get('lei'),
            tickers=data.get('tickers', []),
        )

    def extract_from_text(self, text: str) -> List[Entity]:
        """
        Extract entity references from free text.

        Uses pattern matching to find:
        - Ticker symbols (e.g., $JPM, JPM)
        - Company names
        - Regulator references

        Args:
            text: Free text to search

        Returns:
            List of matched entities (deduplicated)
        """
        found: Set[str] = set()
        entities: List[Entity] = []

        # Pattern: $TICKER or standalone ticker
        ticker_pattern = r'\$?([A-Z]{1,5})(?=\s|$|[.,!?])'
        for match in re.finditer(ticker_pattern, text):
            ticker = match.group(1)
            if ticker in KNOWN_ENTITIES and ticker not in found:
                found.add(ticker)
                entities.append(self._build_entity(ticker))

        # Pattern: Company names (case-insensitive)
        text_lower = text.lower()
        for key, data in KNOWN_ENTITIES.items():
            if key not in found:
                # Check name
                if data['name'].lower() in text_lower:
                    found.add(key)
                    entities.append(self._build_entity(key))
                    continue

                # Check aliases
                for alias in data.get('aliases', []):
                    if len(alias) >= 3:  # Skip short aliases to avoid false positives
                        if re.search(rf'\b{re.escape(alias.lower())}\b', text_lower):
                            found.add(key)
                            entities.append(self._build_entity(key))
                            break

        return entities

    def get_bank_by_cik(self, cik: str) -> Optional[Entity]:
        """Get bank entity by SEC CIK"""
        cik_padded = cik.zfill(10)
        if cik_padded in CIK_MAP:
            return self._build_entity(CIK_MAP[cik_padded])
        return None

    def get_all_banks(self) -> List[Entity]:
        """Get all tracked bank entities"""
        return [
            self._build_entity(key)
            for key, data in KNOWN_ENTITIES.items()
            if data.get('type') == EntityType.BANK
        ]

    def get_all_tickers(self) -> List[str]:
        """Get all tracked tickers"""
        tickers = []
        for data in KNOWN_ENTITIES.values():
            tickers.extend(data.get('tickers', []))
        return list(set(tickers))


# Singleton instance
_resolver: Optional[EntityResolver] = None


def get_resolver() -> EntityResolver:
    """Get or create entity resolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = EntityResolver()
    return _resolver


def resolve_entity(identifier: str) -> Optional[Entity]:
    """Convenience function to resolve an entity"""
    return get_resolver().resolve(identifier)


def extract_entities(text: str) -> List[Entity]:
    """Convenience function to extract entities from text"""
    return get_resolver().extract_from_text(text)
