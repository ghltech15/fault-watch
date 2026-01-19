// Crisis Indicator Definitions for Fault Watch
// Each indicator has thresholds that map to crisis phases

export const CRISIS_PHASES = {
  NORMAL: { level: 0, label: 'NORMAL', color: '#00ff88', description: 'No significant stress detected' },
  ELEVATED: { level: 1, label: 'ELEVATED', color: '#ffd700', description: 'Early warning signs present' },
  WARNING: { level: 2, label: 'WARNING', color: '#ffaa00', description: 'Stress building - days to weeks' },
  SEVERE: { level: 3, label: 'SEVERE', color: '#ff3366', description: 'Imminent risk - hours to days' },
  CRITICAL: { level: 4, label: 'CRITICAL', color: '#ff0040', description: 'Crisis in progress' },
};

export const TIMELINE_ESTIMATES = {
  0: 'Months away',
  1: 'Weeks to months',
  2: 'Days to weeks',
  3: 'Hours to days',
  4: 'IMMINENT',
};

// =============================================================================
// TIER 1: IMMEDIATE WARNING SIGNS (Check Daily)
// =============================================================================

export const TIER1_INDICATORS = {
  SILVER_SPOT_PRICE: {
    id: 'silver_spot',
    name: 'Silver Spot Price',
    category: 'Precious Metals',
    tier: 1,
    unit: '$/oz',
    description: 'COMEX silver spot price - each $1 increase costs shorts ~$212M',
    source: 'COMEX / Live feeds',
    sourceUrl: 'https://www.cmegroup.com/markets/metals/precious/silver.html',
    thresholds: {
      normal: { max: 50, phase: 'NORMAL' },
      elevated: { min: 50, max: 70, phase: 'ELEVATED' },
      warning: { min: 70, max: 90, phase: 'WARNING' },
      severe: { min: 90, max: 100, phase: 'SEVERE' },
      critical: { min: 100, phase: 'CRITICAL' },
    },
    currentValue: 94.00,
    evaluate: (value) => {
      if (value >= 100) return CRISIS_PHASES.CRITICAL;
      if (value >= 90) return CRISIS_PHASES.SEVERE;
      if (value >= 70) return CRISIS_PHASES.WARNING;
      if (value >= 50) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  SILVER_DAILY_CHANGE: {
    id: 'silver_daily',
    name: 'Silver 24h Change',
    category: 'Precious Metals',
    tier: 1,
    unit: '%',
    description: 'Daily percentage move - high volatility signals squeeze intensifying',
    source: 'Market data',
    thresholds: {
      normal: { max: 2, phase: 'NORMAL' },
      elevated: { min: 2, max: 4, phase: 'ELEVATED' },
      warning: { min: 4, max: 7, phase: 'WARNING' },
      severe: { min: 7, max: 10, phase: 'SEVERE' },
      critical: { min: 10, phase: 'CRITICAL' },
    },
    currentValue: 7.14,
    evaluate: (value) => {
      const abs = Math.abs(value);
      if (abs >= 10) return CRISIS_PHASES.CRITICAL;
      if (abs >= 7) return CRISIS_PHASES.SEVERE;
      if (abs >= 4) return CRISIS_PHASES.WARNING;
      if (abs >= 2) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  SHANGHAI_PREMIUM: {
    id: 'shanghai_premium',
    name: 'Shanghai Premium',
    category: 'Physical Market',
    tier: 1,
    unit: '%',
    description: 'Premium of Shanghai physical silver over COMEX - signals paper/physical divergence',
    source: 'Shanghai Gold Exchange',
    sourceUrl: 'https://en.sge.com.cn/data_SilverBenchmarkPrice',
    thresholds: {
      normal: { max: 3, phase: 'NORMAL' },
      elevated: { min: 3, max: 8, phase: 'ELEVATED' },
      warning: { min: 8, max: 12, phase: 'WARNING' },
      severe: { min: 12, max: 15, phase: 'SEVERE' },
      critical: { min: 15, phase: 'CRITICAL' },
    },
    currentValue: 12.0,
    evaluate: (value) => {
      if (value >= 15) return CRISIS_PHASES.CRITICAL;
      if (value >= 12) return CRISIS_PHASES.SEVERE;
      if (value >= 8) return CRISIS_PHASES.WARNING;
      if (value >= 3) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  COMEX_REGISTERED_INVENTORY: {
    id: 'comex_inventory',
    name: 'COMEX Registered Silver',
    category: 'Physical Market',
    tier: 1,
    unit: 'M oz',
    description: 'Silver available for delivery against futures contracts',
    source: 'CME Group',
    sourceUrl: 'https://www.cmegroup.com/delivery_reports/Silver_stocks.xls',
    thresholds: {
      normal: { min: 150, phase: 'NORMAL' },
      elevated: { min: 100, max: 150, phase: 'ELEVATED' },
      warning: { min: 75, max: 100, phase: 'WARNING' },
      severe: { min: 50, max: 75, phase: 'SEVERE' },
      critical: { max: 50, phase: 'CRITICAL' },
    },
    currentValue: 85,
    evaluate: (value) => {
      if (value <= 50) return CRISIS_PHASES.CRITICAL;
      if (value <= 75) return CRISIS_PHASES.SEVERE;
      if (value <= 100) return CRISIS_PHASES.WARNING;
      if (value <= 150) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  BANK_VS_XLF: {
    id: 'bank_vs_xlf',
    name: 'Bank Stock vs XLF',
    category: 'Bank Stress',
    tier: 1,
    unit: '%',
    description: 'Worst performing target bank (C, BAC, JPM) relative to XLF ETF',
    source: 'Market data',
    thresholds: {
      normal: { min: -2, phase: 'NORMAL' },
      elevated: { min: -5, max: -2, phase: 'ELEVATED' },
      warning: { min: -8, max: -5, phase: 'WARNING' },
      severe: { min: -12, max: -8, phase: 'SEVERE' },
      critical: { max: -12, phase: 'CRITICAL' },
    },
    currentValue: -4.2,
    evaluate: (value) => {
      if (value <= -12) return CRISIS_PHASES.CRITICAL;
      if (value <= -8) return CRISIS_PHASES.SEVERE;
      if (value <= -5) return CRISIS_PHASES.WARNING;
      if (value <= -2) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  OFR_STRESS_INDEX: {
    id: 'ofr_fsi',
    name: 'OFR Financial Stress Index',
    category: 'Systemic',
    tier: 1,
    unit: 'index',
    description: 'Official government systemic stress measure - positive = above average stress',
    source: 'Office of Financial Research',
    sourceUrl: 'https://www.financialresearch.gov/financial-stress-index/',
    thresholds: {
      normal: { max: 0, phase: 'NORMAL' },
      elevated: { min: 0, max: 1, phase: 'ELEVATED' },
      warning: { min: 1, max: 2, phase: 'WARNING' },
      severe: { min: 2, max: 4, phase: 'SEVERE' },
      critical: { min: 4, phase: 'CRITICAL' },
    },
    currentValue: 0.3,
    evaluate: (value) => {
      if (value >= 4) return CRISIS_PHASES.CRITICAL;
      if (value >= 2) return CRISIS_PHASES.SEVERE;
      if (value >= 1) return CRISIS_PHASES.WARNING;
      if (value >= 0) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  SOFR_SPREAD: {
    id: 'sofr_spread',
    name: 'SOFR vs Fed Target',
    category: 'Funding',
    tier: 1,
    unit: 'bps',
    description: 'Secured Overnight Financing Rate deviation from Fed target - signals funding stress',
    source: 'FRED',
    sourceUrl: 'https://fred.stlouisfed.org/series/SOFR',
    thresholds: {
      normal: { max: 10, phase: 'NORMAL' },
      elevated: { min: 10, max: 25, phase: 'ELEVATED' },
      warning: { min: 25, max: 50, phase: 'WARNING' },
      severe: { min: 50, max: 100, phase: 'SEVERE' },
      critical: { min: 100, phase: 'CRITICAL' },
    },
    currentValue: 12,
    evaluate: (value) => {
      if (value >= 100) return CRISIS_PHASES.CRITICAL;
      if (value >= 50) return CRISIS_PHASES.SEVERE;
      if (value >= 25) return CRISIS_PHASES.WARNING;
      if (value >= 10) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },
};

// =============================================================================
// TIER 2: CONFIRMING SIGNALS (Check Weekly)
// =============================================================================

export const TIER2_INDICATORS = {
  CDS_SPREAD_CHANGE: {
    id: 'cds_spread',
    name: 'Bank CDS Spread Change',
    category: 'Credit Risk',
    tier: 2,
    unit: 'bps/week',
    description: 'Weekly change in 5Y CDS spreads for C, BAC - market pricing default risk',
    source: 'Bloomberg / S&P Global',
    thresholds: {
      normal: { max: 10, phase: 'NORMAL' },
      elevated: { min: 10, max: 25, phase: 'ELEVATED' },
      warning: { min: 25, max: 50, phase: 'WARNING' },
      severe: { min: 50, max: 100, phase: 'SEVERE' },
      critical: { min: 100, phase: 'CRITICAL' },
    },
    currentValue: null, // Requires Bloomberg terminal
    evaluate: (value) => {
      if (value === null) return { ...CRISIS_PHASES.NORMAL, label: 'UNKNOWN' };
      if (value >= 100) return CRISIS_PHASES.CRITICAL;
      if (value >= 50) return CRISIS_PHASES.SEVERE;
      if (value >= 25) return CRISIS_PHASES.WARNING;
      if (value >= 10) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  INSIDER_SELLING: {
    id: 'insider_selling',
    name: 'Bank Insider Selling',
    category: 'Corporate',
    tier: 2,
    unit: 'transactions',
    description: 'Form 4 filings showing C-suite/director selling at target banks',
    source: 'SEC EDGAR',
    sourceUrl: 'https://www.secform4.com/insider-trading/831001.htm',
    thresholds: {
      normal: { max: 2, phase: 'NORMAL' },
      elevated: { min: 2, max: 5, phase: 'ELEVATED' },
      warning: { min: 5, max: 10, phase: 'WARNING' },
      severe: { min: 10, max: 20, phase: 'SEVERE' },
      critical: { min: 20, phase: 'CRITICAL' },
    },
    currentValue: 3,
    evaluate: (value) => {
      if (value >= 20) return CRISIS_PHASES.CRITICAL;
      if (value >= 10) return CRISIS_PHASES.SEVERE;
      if (value >= 5) return CRISIS_PHASES.WARNING;
      if (value >= 2) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  BANK_PUT_VOLUME: {
    id: 'put_volume',
    name: 'Bank Put Option Volume',
    category: 'Options',
    tier: 2,
    unit: 'x avg',
    description: 'Put option volume relative to 20-day average on C, BAC',
    source: 'Options flow',
    thresholds: {
      normal: { max: 1.5, phase: 'NORMAL' },
      elevated: { min: 1.5, max: 2.5, phase: 'ELEVATED' },
      warning: { min: 2.5, max: 4, phase: 'WARNING' },
      severe: { min: 4, max: 6, phase: 'SEVERE' },
      critical: { min: 6, phase: 'CRITICAL' },
    },
    currentValue: 2.1,
    evaluate: (value) => {
      if (value >= 6) return CRISIS_PHASES.CRITICAL;
      if (value >= 4) return CRISIS_PHASES.SEVERE;
      if (value >= 2.5) return CRISIS_PHASES.WARNING;
      if (value >= 1.5) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  COMEX_DAILY_DRAIN: {
    id: 'comex_drain',
    name: 'COMEX Daily Drain',
    category: 'Physical Market',
    tier: 2,
    unit: 'M oz/day',
    description: 'Rate of inventory reduction from COMEX warehouses',
    source: 'CME Group',
    thresholds: {
      normal: { max: 1, phase: 'NORMAL' },
      elevated: { min: 1, max: 3, phase: 'ELEVATED' },
      warning: { min: 3, max: 5, phase: 'WARNING' },
      severe: { min: 5, max: 8, phase: 'SEVERE' },
      critical: { min: 8, phase: 'CRITICAL' },
    },
    currentValue: 4.2,
    evaluate: (value) => {
      if (value >= 8) return CRISIS_PHASES.CRITICAL;
      if (value >= 5) return CRISIS_PHASES.SEVERE;
      if (value >= 3) return CRISIS_PHASES.WARNING;
      if (value >= 1) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  BACKWARDATION: {
    id: 'backwardation',
    name: 'Futures Backwardation',
    category: 'Futures',
    tier: 2,
    unit: 'boolean',
    description: 'Spot price above futures - signals immediate physical shortage',
    source: 'CME Group',
    currentValue: true,
    evaluate: (value) => {
      return value ? CRISIS_PHASES.WARNING : CRISIS_PHASES.NORMAL;
    },
  },

  CME_MARGIN_HIKES: {
    id: 'margin_hikes',
    name: 'CME Margin Hikes',
    category: 'Exchange',
    tier: 2,
    unit: 'count/month',
    description: 'Number of silver margin requirement increases in past 30 days',
    source: 'CME Group',
    thresholds: {
      normal: { max: 0, phase: 'NORMAL' },
      elevated: { value: 1, phase: 'ELEVATED' },
      warning: { value: 2, phase: 'WARNING' },
      severe: { min: 3, max: 4, phase: 'SEVERE' },
      critical: { min: 5, phase: 'CRITICAL' },
    },
    currentValue: 2,
    evaluate: (value) => {
      if (value >= 5) return CRISIS_PHASES.CRITICAL;
      if (value >= 3) return CRISIS_PHASES.SEVERE;
      if (value >= 2) return CRISIS_PHASES.WARNING;
      if (value >= 1) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  BROKER_RESTRICTIONS: {
    id: 'broker_restrictions',
    name: 'Broker Restrictions',
    category: 'Systemic',
    tier: 2,
    unit: 'count',
    description: 'Number of brokers restricting deposits/trading',
    source: 'News / Social Media',
    thresholds: {
      normal: { max: 0, phase: 'NORMAL' },
      elevated: { value: 1, phase: 'ELEVATED' },
      warning: { value: 2, phase: 'WARNING' },
      severe: { min: 3, max: 4, phase: 'SEVERE' },
      critical: { min: 5, phase: 'CRITICAL' },
    },
    currentValue: 1, // Robinhood
    evaluate: (value) => {
      if (value >= 5) return CRISIS_PHASES.CRITICAL;
      if (value >= 3) return CRISIS_PHASES.SEVERE;
      if (value >= 2) return CRISIS_PHASES.WARNING;
      if (value >= 1) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  LAYOFF_CLUSTERING: {
    id: 'layoffs',
    name: 'Financial Sector Layoffs',
    category: 'Corporate',
    tier: 2,
    unit: 'announcements/week',
    description: 'Major layoff announcements from banks/financials in past 7 days',
    source: 'News',
    thresholds: {
      normal: { max: 1, phase: 'NORMAL' },
      elevated: { min: 1, max: 3, phase: 'ELEVATED' },
      warning: { min: 3, max: 5, phase: 'WARNING' },
      severe: { min: 5, max: 8, phase: 'SEVERE' },
      critical: { min: 8, phase: 'CRITICAL' },
    },
    currentValue: 4, // Citi, BlackRock, others
    evaluate: (value) => {
      if (value >= 8) return CRISIS_PHASES.CRITICAL;
      if (value >= 5) return CRISIS_PHASES.SEVERE;
      if (value >= 3) return CRISIS_PHASES.WARNING;
      if (value >= 1) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },
};

// =============================================================================
// TIER 3: PRE-CRISIS INDICATORS (Watch for News)
// =============================================================================

export const TIER3_INDICATORS = {
  FED_DISCOUNT_WINDOW: {
    id: 'discount_window',
    name: 'Fed Discount Window Usage',
    category: 'Fed Facilities',
    tier: 3,
    unit: '$B',
    description: 'Emergency Fed lending to banks - any usage is a red flag',
    source: 'Fed H.4.1 Report',
    sourceUrl: 'https://www.federalreserve.gov/releases/h41/',
    thresholds: {
      normal: { max: 0, phase: 'NORMAL' },
      elevated: { min: 0, max: 5, phase: 'ELEVATED' },
      warning: { min: 5, max: 20, phase: 'WARNING' },
      severe: { min: 20, max: 50, phase: 'SEVERE' },
      critical: { min: 50, phase: 'CRITICAL' },
    },
    currentValue: 0,
    evaluate: (value) => {
      if (value >= 50) return CRISIS_PHASES.CRITICAL;
      if (value >= 20) return CRISIS_PHASES.SEVERE;
      if (value >= 5) return CRISIS_PHASES.WARNING;
      if (value > 0) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  SRF_USAGE: {
    id: 'srf_usage',
    name: 'Standing Repo Facility',
    category: 'Fed Facilities',
    tier: 3,
    unit: '$B',
    description: 'Fed repo lending to primary dealers - spikes indicate liquidity stress',
    source: 'NY Fed',
    sourceUrl: 'https://www.newyorkfed.org/markets/desk-operations/repo',
    thresholds: {
      normal: { max: 10, phase: 'NORMAL' },
      elevated: { min: 10, max: 30, phase: 'ELEVATED' },
      warning: { min: 30, max: 50, phase: 'WARNING' },
      severe: { min: 50, max: 100, phase: 'SEVERE' },
      critical: { min: 100, phase: 'CRITICAL' },
    },
    currentValue: 0, // Post year-end normalized
    evaluate: (value) => {
      if (value >= 100) return CRISIS_PHASES.CRITICAL;
      if (value >= 50) return CRISIS_PHASES.SEVERE;
      if (value >= 30) return CRISIS_PHASES.WARNING;
      if (value >= 10) return CRISIS_PHASES.ELEVATED;
      return CRISIS_PHASES.NORMAL;
    },
  },

  CREDIT_RATING_WATCH: {
    id: 'rating_watch',
    name: 'Credit Rating Actions',
    category: 'Credit',
    tier: 3,
    unit: 'boolean',
    description: 'Moody\'s/S&P/Fitch negative watch or downgrade on target banks',
    source: 'Rating agencies',
    currentValue: false,
    evaluate: (value) => {
      return value ? CRISIS_PHASES.SEVERE : CRISIS_PHASES.NORMAL;
    },
  },

  DIVIDEND_CUTS: {
    id: 'dividend_cuts',
    name: 'Dividend Cuts/Suspensions',
    category: 'Corporate',
    tier: 3,
    unit: 'count',
    description: 'Banks cutting or suspending dividends to preserve capital',
    source: 'Corporate announcements',
    currentValue: 0,
    evaluate: (value) => {
      if (value >= 3) return CRISIS_PHASES.CRITICAL;
      if (value >= 2) return CRISIS_PHASES.SEVERE;
      if (value >= 1) return CRISIS_PHASES.WARNING;
      return CRISIS_PHASES.NORMAL;
    },
  },

  CREDIT_FACILITY_DRAWDOWN: {
    id: 'credit_drawdown',
    name: 'Credit Facility Drawdowns',
    category: 'Corporate',
    tier: 3,
    unit: 'count',
    description: 'Banks tapping emergency credit lines - 8-K filings',
    source: 'SEC EDGAR 8-K',
    currentValue: 0,
    evaluate: (value) => {
      if (value >= 2) return CRISIS_PHASES.CRITICAL;
      if (value >= 1) return CRISIS_PHASES.SEVERE;
      return CRISIS_PHASES.NORMAL;
    },
  },

  INTERBANK_FREEZE: {
    id: 'interbank_freeze',
    name: 'Interbank Lending Freeze',
    category: 'Systemic',
    tier: 3,
    unit: 'boolean',
    description: 'Banks refusing to lend to each other - ultimate stress signal',
    source: 'News / Fed commentary',
    currentValue: false,
    evaluate: (value) => {
      return value ? CRISIS_PHASES.CRITICAL : CRISIS_PHASES.NORMAL;
    },
  },
};

// =============================================================================
// BANK-SPECIFIC EXPOSURE DATA
// =============================================================================

export const BANK_EXPOSURE = {
  C: {
    ticker: 'C',
    name: 'Citigroup',
    marketCap: 120, // $B
    pmDerivatives: 142.8, // $B from OCC
    rumoredShort: 3400, // M oz (unverified)
    verifiedShort: null,
    lossPerDollar: 3400, // M oz * $1 = $3.4B per $1 silver move (if rumors true)
  },
  BAC: {
    ticker: 'BAC',
    name: 'Bank of America',
    marketCap: 350,
    pmDerivatives: 61.7,
    rumoredShort: 1000,
    verifiedShort: null,
    lossPerDollar: 1000,
  },
  JPM: {
    ticker: 'JPM',
    name: 'JPMorgan Chase',
    marketCap: 650,
    pmDerivatives: 323.5,
    rumoredShort: null, // Reportedly flipped net long
    verifiedShort: null,
    notes: 'Reportedly net LONG as of recent CFTC data',
  },
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export const getAllIndicators = () => ({
  ...TIER1_INDICATORS,
  ...TIER2_INDICATORS,
  ...TIER3_INDICATORS,
});

export const calculateOverallCrisisLevel = (indicators) => {
  const allIndicators = Object.values(indicators);
  const levels = allIndicators
    .map(ind => ind.evaluate(ind.currentValue))
    .filter(phase => phase.label !== 'UNKNOWN');
  
  if (levels.length === 0) return CRISIS_PHASES.NORMAL;
  
  // Weight Tier 1 indicators more heavily
  const tier1Levels = allIndicators
    .filter(ind => ind.tier === 1)
    .map(ind => ind.evaluate(ind.currentValue).level);
  
  const avgTier1 = tier1Levels.reduce((a, b) => a + b, 0) / tier1Levels.length;
  const maxLevel = Math.max(...levels.map(l => l.level));
  
  // Use combination of average Tier 1 and max overall
  const weightedLevel = Math.round((avgTier1 * 0.6) + (maxLevel * 0.4));
  
  const phases = Object.values(CRISIS_PHASES);
  return phases.find(p => p.level === weightedLevel) || CRISIS_PHASES.NORMAL;
};

export const getTimelineEstimate = (crisisLevel) => {
  return TIMELINE_ESTIMATES[crisisLevel] || 'Unknown';
};
