"""
Crisis Gauge Module for fault.watch API
Comprehensive crack monitoring system for banking crisis detection.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class CrackStatus(str, Enum):
    """Status of each crack indicator."""
    CLEAR = "clear"
    WATCHING = "watching"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CrackIndicator(BaseModel):
    """Individual crack indicator."""
    id: str
    name: str
    description: str
    status: CrackStatus
    value: Optional[str] = None
    threshold: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    last_updated: Optional[str] = None


class ExposureLoss(BaseModel):
    """Loss calculation for a specific exposure level."""
    entity: str
    exposure_oz: float
    exposure_label: str
    loss_per_dollar: float
    total_loss: float
    loss_label: str
    market_cap: Optional[float] = None
    loss_vs_cap_pct: Optional[float] = None
    is_verified: bool = False


class PhaseIndicator(BaseModel):
    """Phase progression indicator."""
    id: str
    description: str
    status: bool
    source: Optional[str] = None


class CrisisPhase(BaseModel):
    """Crisis phase with indicators."""
    phase: int
    name: str
    description: str
    indicators: List[PhaseIndicator]
    progress_pct: float


class CrisisGaugeData(BaseModel):
    """Complete crisis gauge data."""
    silver_price: float
    silver_base_price: float = 30.0
    silver_move: float
    losses: List[ExposureLoss]
    total_aggregate_loss: float
    tier1_cracks: List[CrackIndicator]
    tier2_cracks: List[CrackIndicator]
    tier3_cracks: List[CrackIndicator]
    phases: List[CrisisPhase]
    current_phase: int
    cracks_showing_count: int
    total_cracks: int
    crisis_probability: float
    crisis_level: str
    crisis_color: str
    resources: List[Dict[str, str]]


def calculate_exposure_losses(silver_price: float, base_price: float = 30.0) -> List[ExposureLoss]:
    """Calculate losses for various exposure levels."""
    move = silver_price - base_price

    exposures = [
        {'entity': 'COMEX Aggregate', 'oz': 212_000_000, 'market_cap': None, 'verified': True},
        {'entity': 'Bank of America (rumored)', 'oz': 1_000_000_000, 'market_cap': 350_000_000_000, 'verified': False},
        {'entity': 'Citigroup (rumored)', 'oz': 3_400_000_000, 'market_cap': 120_000_000_000, 'verified': False},
        {'entity': 'Morgan Stanley', 'oz': 300_000_000, 'market_cap': 180_000_000_000, 'verified': False},
    ]

    losses = []
    for exp in exposures:
        loss = exp['oz'] * move
        loss_vs_cap = (loss / exp['market_cap'] * 100) if exp['market_cap'] else None

        losses.append(ExposureLoss(
            entity=exp['entity'],
            exposure_oz=exp['oz'],
            exposure_label=f"{exp['oz'] / 1e9:.1f}B oz" if exp['oz'] >= 1e9 else f"{exp['oz'] / 1e6:.0f}M oz",
            loss_per_dollar=exp['oz'],
            total_loss=loss,
            loss_label=f"${loss / 1e9:.1f}B" if loss >= 1e9 else f"${loss / 1e6:.0f}M",
            market_cap=exp['market_cap'],
            loss_vs_cap_pct=loss_vs_cap,
            is_verified=exp['verified']
        ))

    return losses


def get_tier1_cracks(prices: dict) -> List[CrackIndicator]:
    """Tier 1: Immediate warning signs - check daily."""
    cracks = []

    # Bank stock vs XLF
    xlf = prices.get('financials', {})
    citi = prices.get('citigroup', {})
    bac = prices.get('bank_of_america', {})

    xlf_chg = xlf.change_pct if hasattr(xlf, 'change_pct') else 0
    citi_chg = citi.change_pct if hasattr(citi, 'change_pct') else 0
    bac_chg = bac.change_pct if hasattr(bac, 'change_pct') else 0

    bank_underperform = citi_chg < xlf_chg - 2 or bac_chg < xlf_chg - 2

    cracks.append(CrackIndicator(
        id='bank_vs_xlf',
        name='Bank Stock vs XLF',
        description='Individual bank weakness relative to financial sector',
        status=CrackStatus.WARNING if bank_underperform else CrackStatus.WATCHING,
        value=f"C: {citi_chg:.1f}%, BAC: {bac_chg:.1f}% vs XLF: {xlf_chg:.1f}%",
        threshold='Underperform XLF by >2%',
        source='Live market data'
    ))

    # OFR Financial Stress Index
    cracks.append(CrackIndicator(
        id='ofr_stress',
        name='OFR Financial Stress Index',
        description='33 systemic stress variables',
        status=CrackStatus.WATCHING,
        value='Monitor daily',
        threshold='Sustained increase',
        source='Office of Financial Research',
        source_url='https://www.financialresearch.gov/financial-stress-index/'
    ))

    # SOFR Rate
    cracks.append(CrackIndicator(
        id='sofr_rate',
        name='SOFR Rate Spikes',
        description='Overnight funding stress',
        status=CrackStatus.CLEAR,
        value='Normal range',
        threshold='>50bp above Fed target',
        source='FRED',
        source_url='https://fred.stlouisfed.org/series/SOFR'
    ))

    # Repo Facility
    cracks.append(CrackIndicator(
        id='repo_usage',
        name='Fed Repo Facility Usage',
        description='Banks needing emergency cash',
        status=CrackStatus.CLEAR,
        value='Normalized',
        threshold='Mid-month spikes',
        source='NY Fed',
        source_url='https://www.newyorkfed.org/markets/desk-operations/repo'
    ))

    # Silver Acceleration
    silver = prices.get('silver', {})
    silver_price = silver.price if hasattr(silver, 'price') else 0
    silver_chg = silver.change_pct if hasattr(silver, 'change_pct') else 0

    if silver_price >= 100:
        silver_status = CrackStatus.CRITICAL
    elif silver_price >= 90:
        silver_status = CrackStatus.WARNING
    elif silver_price >= 80:
        silver_status = CrackStatus.WATCHING
    else:
        silver_status = CrackStatus.CLEAR

    cracks.append(CrackIndicator(
        id='silver_acceleration',
        name='Silver Price Acceleration',
        description='Squeeze intensity',
        status=silver_status,
        value=f"${silver_price:.2f} ({silver_chg:+.1f}% today)",
        threshold='$90+ warning, $100+ critical',
        source='Live spot prices',
        source_url='https://tradingeconomics.com/commodity/silver'
    ))

    return cracks


def get_tier2_cracks(prices: dict) -> List[CrackIndicator]:
    """Tier 2: Confirming signals - check weekly."""
    return [
        CrackIndicator(
            id='cds_spreads',
            name='CDS Spread Widening',
            description='Market pricing in default risk',
            status=CrackStatus.UNKNOWN,
            value='Requires Bloomberg Terminal',
            threshold='>50 bps weekly move',
            source='Bloomberg Terminal'
        ),
        CrackIndicator(
            id='insider_selling',
            name='Insider Selling (Form 4)',
            description='Executives dumping stock',
            status=CrackStatus.WATCHING,
            value='Check for unusual volume',
            threshold='C-suite sales clustering',
            source='OpenInsider',
            source_url='https://openinsider.com'
        ),
        CrackIndicator(
            id='bank_bond_yields',
            name='Bank Bond Yields vs Treasuries',
            description='Credit risk perception',
            status=CrackStatus.WATCHING,
            value='Monitor spread',
            threshold='Spread widening >25 bps',
            source='Bond market data'
        ),
        CrackIndicator(
            id='put_volume',
            name='Options Put Volume',
            description='Smart money hedging',
            status=CrackStatus.WATCHING,
            value='Monitor C, BAC puts',
            threshold='Unusual put buying',
            source='Options flow analysis'
        ),
        CrackIndicator(
            id='comex_drain',
            name='COMEX Inventory Drain',
            description='Physical metal leaving',
            status=CrackStatus.WARNING,
            value='-70% since 2020',
            threshold='<5M oz drain/day',
            source='CME Daily Reports',
            source_url='https://www.cmegroup.com/delivery_reports/Silver_stocks.xls'
        ),
    ]


def get_tier3_cracks(prices: dict) -> List[CrackIndicator]:
    """Tier 3: Pre-crisis indicators - watch for news."""
    return [
        CrackIndicator(
            id='credit_watch',
            name='Credit Rating Watch',
            description='Rating agencies see trouble',
            status=CrackStatus.CLEAR,
            value='No current watches',
            threshold="Moody's/S&P/Fitch announcements",
            source='Rating agencies'
        ),
        CrackIndicator(
            id='discount_window',
            name='Fed Discount Window Usage',
            description="Banks can't get market funding",
            status=CrackStatus.CLEAR,
            value='Normal levels',
            threshold='Unusual mid-month spikes',
            source='Fed H.4.1 Report',
            source_url='https://www.federalreserve.gov/releases/h41/'
        ),
        CrackIndicator(
            id='credit_facility',
            name='Credit Facility Drawdowns',
            description='Banks tapping emergency lines',
            status=CrackStatus.CLEAR,
            value='Monitor 8-K filings',
            threshold='Emergency line usage',
            source='SEC 8-K Filings'
        ),
        CrackIndicator(
            id='interbank_freeze',
            name='Interbank Lending Freeze',
            description="Banks won't lend to each other",
            status=CrackStatus.CLEAR,
            value='Normal activity',
            threshold='Fed liquidity commentary',
            source='Financial news'
        ),
        CrackIndicator(
            id='dividend_cuts',
            name='Dividend Cut/Suspension',
            description='Banks preserving cash',
            status=CrackStatus.CLEAR,
            value='No announcements',
            threshold='Corporate announcements',
            source='Press releases'
        ),
    ]


def get_crisis_phases() -> List[CrisisPhase]:
    """Get crisis phase progression."""
    phases = [
        CrisisPhase(
            phase=1,
            name='Hidden Stress',
            description='Internal pressure building, not visible to public',
            indicators=[
                PhaseIndicator(id='layoffs', description='Layoff announcements clustering (Citi, BlackRock)', status=True),
                PhaseIndicator(id='efficiency', description='"Efficiency" language on earnings calls', status=True),
                PhaseIndicator(id='underperform', description='Stock underperforming despite beats', status=True),
                PhaseIndicator(id='broker_restrict', description='Broker restrictions (Robinhood)', status=True),
                PhaseIndicator(id='insider_selling', description='Unusual insider selling', status=False),
            ],
            progress_pct=80.0
        ),
        CrisisPhase(
            phase=2,
            name='Market Stress',
            description='Days to weeks before - smart money exits',
            indicators=[
                PhaseIndicator(id='cds_blowout', description='CDS spreads blow out (>100 bps)', status=False),
                PhaseIndicator(id='gap_down', description='Stock gap down >5% on no news', status=False),
                PhaseIndicator(id='downgrade_watch', description='Credit downgrade watch', status=False),
                PhaseIndicator(id='bond_spike', description='Bond yields spike vs peers', status=False),
                PhaseIndicator(id='put_explosion', description='Put volume explodes', status=False),
            ],
            progress_pct=0.0
        ),
        CrisisPhase(
            phase=3,
            name='Liquidity Crisis',
            description='Days before failure - emergency measures',
            indicators=[
                PhaseIndicator(id='fed_spike', description='Fed facility usage spikes', status=False),
                PhaseIndicator(id='deposit_flight', description='Deposit flight rumors', status=False),
                PhaseIndicator(id='credit_drawdown', description='Credit line drawdowns', status=False),
                PhaseIndicator(id='trading_halt', description='Trading halts', status=False),
                PhaseIndicator(id='emergency_announce', description='Emergency announcements', status=False),
            ],
            progress_pct=0.0
        ),
        CrisisPhase(
            phase=4,
            name='Public Crisis',
            description='Systemic event - government intervention',
            indicators=[
                PhaseIndicator(id='gov_statement', description='Gov/Fed coordinated statements', status=False),
                PhaseIndicator(id='emergency_cuts', description='Emergency rate cuts', status=False),
                PhaseIndicator(id='counterparty', description='Counterparty exposure news', status=False),
                PhaseIndicator(id='fdic', description='FDIC involvement', status=False),
            ],
            progress_pct=0.0
        ),
    ]

    for phase in phases:
        confirmed = sum(1 for i in phase.indicators if i.status)
        phase.progress_pct = (confirmed / len(phase.indicators)) * 100

    return phases


def get_crisis_resources() -> List[Dict[str, str]]:
    """Get monitoring resources."""
    return [
        {'name': 'OFR Financial Stress Index', 'tracks': '33 systemic stress variables', 'url': 'https://www.financialresearch.gov/financial-stress-index/'},
        {'name': 'NY Fed Repo Operations', 'tracks': 'Fed emergency lending', 'url': 'https://www.newyorkfed.org/markets/desk-operations/repo'},
        {'name': 'FRED SOFR Rate', 'tracks': 'Overnight funding cost', 'url': 'https://fred.stlouisfed.org/series/SOFR'},
        {'name': 'COMEX Silver Inventory', 'tracks': 'Physical metal drain', 'url': 'https://www.cmegroup.com/delivery_reports/Silver_stocks.xls'},
        {'name': 'SEC Form 4 Filings', 'tracks': 'Insider transactions', 'url': 'https://openinsider.com'},
        {'name': 'Trading Economics Silver', 'tracks': 'Live silver spot', 'url': 'https://tradingeconomics.com/commodity/silver'},
    ]


def build_crisis_gauge(prices: dict) -> CrisisGaugeData:
    """Build complete crisis gauge data."""
    silver = prices.get('silver', type('obj', (object,), {'price': 30, 'change_pct': 0})())
    silver_price = silver.price if hasattr(silver, 'price') else 30
    base_price = 30.0

    losses = calculate_exposure_losses(silver_price, base_price)
    total_loss = sum(l.total_loss for l in losses if l.is_verified)

    tier1 = get_tier1_cracks(prices)
    tier2 = get_tier2_cracks(prices)
    tier3 = get_tier3_cracks(prices)

    all_cracks = tier1 + tier2 + tier3
    cracks_showing = sum(1 for c in all_cracks if c.status in [CrackStatus.WARNING, CrackStatus.CRITICAL])

    phases = get_crisis_phases()
    current_phase = 1
    for phase in phases:
        if phase.progress_pct >= 50:
            current_phase = phase.phase

    phase1_progress = phases[0].progress_pct if phases else 0
    crisis_probability = min(100, (cracks_showing / len(all_cracks)) * 100 + phase1_progress * 0.3)

    if current_phase >= 4:
        crisis_level, crisis_color = "Public Crisis", "#e31837"
    elif current_phase >= 3:
        crisis_level, crisis_color = "Liquidity Crisis", "#e31837"
    elif current_phase >= 2 or crisis_probability >= 50:
        crisis_level, crisis_color = "Market Stress", "#ff8c42"
    else:
        crisis_level, crisis_color = "Hidden Stress", "#fbbf24"

    return CrisisGaugeData(
        silver_price=silver_price,
        silver_base_price=base_price,
        silver_move=silver_price - base_price,
        losses=losses,
        total_aggregate_loss=total_loss,
        tier1_cracks=tier1,
        tier2_cracks=tier2,
        tier3_cracks=tier3,
        phases=phases,
        current_phase=current_phase,
        cracks_showing_count=cracks_showing,
        total_cracks=len(all_cracks),
        crisis_probability=crisis_probability,
        crisis_level=crisis_level,
        crisis_color=crisis_color,
        resources=get_crisis_resources()
    )
