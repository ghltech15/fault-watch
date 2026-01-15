const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PriceData {
  price: number
  prev_close?: number
  change_pct: number
  week_change: number
}

export interface CountdownData {
  days: number
  hours: number
  minutes: number
  expired: boolean
  deadline: string
  label: string
}

export interface SourceReference {
  name: string
  tier: 1 | 2 | 3
  url?: string
}

export interface AlertData {
  level: 'critical' | 'warning' | 'info'
  title: string
  detail: string
  action?: string
  // Verification fields
  verification_status: 'verified' | 'partial' | 'theory' | 'unverified'
  source_count: number
  sources: SourceReference[]
  is_hypothetical: boolean
}

export interface TheoryData {
  id: string
  title: string
  hypothesis: string
  basis: string[]
  confidence: number
  status: 'theory' | 'partial'
  trigger_conditions: string[]
  sources: SourceReference[]
}

export interface DominoStatus {
  id: string
  label: string
  status: string
  color: string
  detail: string
}

export interface BankData {
  name: string
  ticker: string
  position?: string
  ounces?: number
  equity: number
  pm_derivatives?: number
  current_price?: number
  daily_change?: number
  paper_loss?: number
}

export interface DashboardData {
  risk_index: number
  risk_label: string
  risk_color: string
  prices: Record<string, PriceData>
  countdowns: Record<string, CountdownData>
  alerts: AlertData[]
  dominoes: DominoStatus[]
  stress_level: number
  last_updated: string
}

export interface ScenarioData {
  silver_price: number
  ms_loss: number
  citi_loss: number
  jpm_gain: number
  total_short_loss: number
  ms_insolvent: boolean
  citi_insolvent: boolean
  fed_coverage_pct: number
}

// Contagion Data Types
export interface CreditStressData {
  ted_spread: number | null
  credit_spread: number | null
  high_yield_spread: number | null
  sofr_rate: number | null
  stress_level: string
  stress_score: number
}

export interface LiquidityData {
  reverse_repo: number | null
  bank_deposits: number | null
  deposit_change_pct: number | null
  commercial_paper: number | null
  liquidity_score: number
}

export interface DelinquencyData {
  credit_card: number | null
  auto_loan: number | null
  mortgage: number | null
  trend: string
}

export interface ComexData {
  registered_oz: number | null
  eligible_oz: number | null
  total_oz: number | null
  open_interest_oz: number | null
  coverage_ratio: number | null
  days_of_supply: number | null
  status: string
}

export interface ContagionSector {
  id: string
  name: string
  etf: string | null
  inverse_etf: string | null
  current_price: number | null
  change_pct: number | null
  week_change: number | null
  why_collapse: string
  investment_plays: string[]
  risk_level: string
  contagion_score: number
}

export interface JuniorMiner {
  ticker: string
  name: string
  price: number | null
  change_pct: number | null
  leverage_level: string
  potential_multiple: string | null
}

export interface ContagionRiskData {
  contagion_score: number
  contagion_level: string
  contagion_color: string
  credit_stress: CreditStressData
  liquidity: LiquidityData
  delinquencies: DelinquencyData
  comex: ComexData
  sectors: ContagionSector[]
  junior_miners: JuniorMiner[]
  cascade_stage: number
  cascade_description: string
  last_updated: string
}

export interface CascadeData {
  stage: number
  description: string
  stages: Record<string, string>
}

export interface OpportunityPlay {
  type: string
  ticker: string
  name: string
  price: number | null
  thesis: string
  risk: string
}

export interface OpportunitiesData {
  under_100: OpportunityPlay[]
  under_500: OpportunityPlay[]
  leveraged: OpportunityPlay[]
  sectors_at_risk: Array<{
    sector: string
    risk_level: string
    plays: string[]
  }>
  disclaimer: string
}

// Naked Short Analysis Types
export interface BankShortPosition {
  name: string
  ticker: string
  position: 'SHORT' | 'LONG'
  ounces: number
  equity: number
  insolvency_price: number | null
  deadline: string | null
  regulator: string | null
  loss_ratio_at_80: number | null
  note: string | null
}

export interface NakedShortAnalysis {
  total_short_oz: number
  available_physical_oz: number
  paper_to_physical_ratio: number
  years_of_production: number
  verdict: string
  bank_positions: BankShortPosition[]
  total_short_value_at_current: number
  total_short_value_at_80: number
  total_short_value_at_100: number
  banks_insolvent_at_80: string[]
  banks_insolvent_at_100: string[]
  lloyds_deadline: string
  sec_deadline: string
}

async function fetchAPI<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`)
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`)
  }
  return res.json()
}

// Pipeline Types
export interface PipelineStatus {
  status: string
  modules: Record<string, boolean>
  last_refresh: string | null
}

export interface StressIndicators {
  stress_score: number
  status: string
  indicators: string[]
  fed_stress: {
    ted_spread: number | null
    high_yield_spread: number | null
    reverse_repo: number | null
    fed_funds_rate: number | null
    timestamp: string
  }
  comex_status: string
  timestamp: string
}

export interface SECFiling {
  company: string
  cik: string
  form_type: string
  filed_date: string
  accession_number: string
  filing_url: string
  description: string
  keywords_found: string[]
  is_critical: boolean
}

export interface SECData {
  total_filings_7d: number
  critical_filings: number
  monitored_companies: number
  recent_critical: SECFiling[]
  last_updated: string
}

export interface PipelineAlert {
  id: string
  severity: string
  severity_level: number
  type: string
  title: string
  description: string
  source: string
  source_url: string | null
  related_entity: string | null
  data: Record<string, unknown>
  timestamp: string
  acknowledged: boolean
  notified: boolean
}

export interface AlertSummary {
  total_alerts: number
  last_24h: number
  critical: number
  high: number
  unacknowledged: number
  by_type: Record<string, number>
}

export interface PipelineAlerts {
  alerts: PipelineAlert[]
  critical: PipelineAlert[]
  summary: AlertSummary
}

export interface SocialData {
  total_posts_fetched: number
  trending_posts: number
  sentiment: {
    bullish_pct: number
    bearish_pct: number
    neutral_pct: number
    total_posts: number
    avg_score: number
  }
  top_posts: Array<{
    id: string
    title: string
    subreddit: string
    score: number
    num_comments: number
    url: string
    permalink: string
  }>
  subreddits_monitored: number
  last_updated: string
}

export interface NewsArticle {
  title: string
  description: string
  url: string
  source: string
  author: string | null
  published_date: string
  categories: string[]
  content: string
}

export interface NewsData {
  total_relevant: number
  precious_metals_news: number
  bank_news: number
  crisis_indicators: number
  breaking_news: number
  top_stories: NewsArticle[]
  coverage_analysis: {
    total_articles: number
    relevant_articles: number
    by_source: Record<string, number>
    keyword_frequency: Record<string, number>
  }
  last_updated: string
}

export interface DealerData {
  silver: {
    spot_price: number | null
    avg_premium_pct: number
    min_premium_pct: number
    max_premium_pct: number
    products_in_stock: number
    products_out_of_stock: number
    out_of_stock_rate: number
  }
  gold: {
    spot_price: number | null
    avg_premium_pct: number
    min_premium_pct: number
    max_premium_pct: number
    products_in_stock: number
    products_out_of_stock: number
    out_of_stock_rate: number
  }
  availability: {
    silver: { in_stock: number; out_of_stock: number; availability_rate: number }
    gold: { in_stock: number; out_of_stock: number; availability_rate: number }
    timestamp: string
  }
  best_silver_deals: Array<{
    dealer: string
    product_name: string
    price: number
    premium_pct: number
  }>
  dealers_monitored: number
  last_updated: string
}

export interface RegulatoryRelease {
  source: string
  title: string
  release_type: string
  date: string
  url: string
  description: string
  keywords_found: string[]
  is_critical: boolean
}

export interface RegulatoryData {
  total_releases_7d: number
  critical_releases: number
  recent_critical: RegulatoryRelease[]
  cot_silver: {
    report_date: string
    metal: string
    commercial_net: number
    non_commercial_net: number
    total_open_interest: number
  } | null
  sources_monitored: number
  last_updated: string
}

export interface BankExposureSummary {
  bank_count: number
  banks_dropping: number
  troubled_banks: Array<{
    bank: string
    ticker: string
    price: number
    change_pct: number
  }>
  timestamp: string
}

export const api = {
  getDashboard: () => fetchAPI<DashboardData>('/api/dashboard'),
  getPrices: () => fetchAPI<Record<string, PriceData>>('/api/prices'),
  getCountdowns: () => fetchAPI<Record<string, CountdownData>>('/api/countdowns'),
  getAlerts: () => fetchAPI<AlertData[]>('/api/alerts'),
  getTheories: () => fetchAPI<TheoryData[]>('/api/theories'),
  getBanks: () => fetchAPI<BankData[]>('/api/banks'),
  getDominoes: () => fetchAPI<DominoStatus[]>('/api/dominoes'),
  getScenario: (price: number) => fetchAPI<ScenarioData>(`/api/scenarios/${price}`),
  getScenarios: () => fetchAPI<Record<string, ScenarioData>>('/api/scenarios'),
  // Naked short analysis
  getNakedShorts: () => fetchAPI<NakedShortAnalysis>('/api/naked-shorts'),
  // Contagion endpoints
  getContagion: () => fetchAPI<ContagionRiskData>('/api/contagion'),
  getCreditStress: () => fetchAPI<CreditStressData>('/api/contagion/credit'),
  getLiquidity: () => fetchAPI<LiquidityData>('/api/contagion/liquidity'),
  getDelinquencies: () => fetchAPI<DelinquencyData>('/api/contagion/delinquencies'),
  getComex: () => fetchAPI<ComexData>('/api/contagion/comex'),
  getSectors: () => fetchAPI<ContagionSector[]>('/api/contagion/sectors'),
  getCascade: () => fetchAPI<CascadeData>('/api/cascade'),
  getMiners: () => fetchAPI<JuniorMiner[]>('/api/miners'),
  getOpportunities: () => fetchAPI<OpportunitiesData>('/api/opportunities'),

  // Pipeline endpoints (new data pipeline)
  getPipelineStatus: () => fetchAPI<PipelineStatus>('/api/pipeline/status'),
  getPipelineData: () => fetchAPI<Record<string, unknown>>('/api/pipeline/data'),
  refreshPipeline: () => fetch(`${API_BASE}/api/pipeline/refresh`, { method: 'POST' }).then(r => r.json()),
  getStressIndicators: () => fetchAPI<StressIndicators>('/api/pipeline/stress'),
  getSECFilings: () => fetchAPI<SECData>('/api/pipeline/sec'),
  getCriticalSECFilings: () => fetchAPI<SECFiling[]>('/api/pipeline/sec/critical'),
  getPipelineAlerts: () => fetchAPI<PipelineAlerts>('/api/pipeline/alerts'),
  checkAlerts: () => fetch(`${API_BASE}/api/pipeline/alerts/check`, { method: 'POST' }).then(r => r.json()),
  getSocialData: () => fetchAPI<SocialData>('/api/pipeline/social'),
  getNewsData: () => fetchAPI<NewsData>('/api/pipeline/news'),
  getBreakingNews: () => fetchAPI<NewsArticle[]>('/api/pipeline/news/breaking'),
  getDealerData: () => fetchAPI<DealerData>('/api/pipeline/dealers'),
  getRegulatoryData: () => fetchAPI<RegulatoryData>('/api/pipeline/regulatory'),
  getBankExposureSummary: () => fetchAPI<BankExposureSummary>('/api/pipeline/banks'),
  getCrisisGauge: () => fetchAPI<CrisisGaugeData>('/api/crisis-gauge'),
  // Crisis Scanner - 5 minute refresh
  getCrisisScanner: () => fetchAPI<CrisisScannerData>('/api/crisis-scanner'),
  // Global physical silver prices
  getGlobalPhysical: () => fetchAPI<GlobalPhysicalData>('/api/watchlist/global-physical'),
}

// Global Physical Silver Prices
export interface PhysicalPriceLocation {
  price: number
  premium_pct: number
  premium_usd: number
  label: string
  status: 'normal' | 'elevated' | 'critical'
  source: string
}

export interface GlobalPhysicalData {
  comex_spot: {
    price: number
    label: string
    source: string
  }
  shanghai: PhysicalPriceLocation
  dubai: PhysicalPriceLocation
  tokyo: PhysicalPriceLocation
  london: PhysicalPriceLocation
  us_retail: PhysicalPriceLocation
  timestamp: string
  note: string
}

// Crisis Scanner Types (matches backend response)
export interface CrisisScannerData {
  scan_metadata: {
    scan_id: string
    scan_date: string
    scan_timestamp: string
    analyst: string
    version: string
  }
  system_status: {
    alert_level: 'CRITICAL' | 'HIGH' | 'ELEVATED' | 'MODERATE' | 'LOW'
    alert_level_code: number
    primary_drivers: string[]
    recommended_action: string
  }
  silver_market: {
    price_data: {
      spot_price: number
      user_tracked_high: number
      user_tracked_low: number
      recovery_from_low_pct: number
      user_thesis: string
    }
    market_structure: {
      backwardation: boolean
      backwardation_status: string
      verification: string
      source: string
      significance: string
    }
    comex_inventory: {
      registered_oz: number
      registered_tons: number
      trend: string
      verification: string
      source: string
      as_of_date: string
    }
    delivery_activity: {
      date: string
      contracts_delivered: number
      ounces_delivered: number
      primary_issuer: string
      issuer_percentage: number
      verification: string
      source: string
      significance: string
    }
    supply_deficit: {
      year: number
      deficit_oz: number
      consecutive_deficit_years: number
      projected_2026_deficit_oz: number
      verification: string
      sources: string[]
    }
    china_export_curbs: {
      effective_date: string
      impact_description: string
      verification: string
      sources: string[]
    }
    physical_premium_reports: {
      tokyo_premium_claimed: number
      dubai_premium_claimed: string
      verification: string
      note: string
    }
  }
  federal_reserve: {
    standing_repo_facility: {
      current_balance: number
      daily_limit: string
      limit_change_date: string
      previous_limit: number
      verification: string
      source: string
      significance: string
    }
    year_end_spike: {
      date: string
      amount: number
      treasury_collateral: number
      mbs_collateral: number
      previous_record: number
      status: string
      resolution_date: string
      verification: string
      source: string
      significance: string
    }
    reverse_repo: {
      current_balance: number
      year_end_spike: number
      verification: string
      source: string
    }
    quantitative_tightening: {
      status: string
      end_date: string
      total_reduction: number
      verification: string
    }
  }
  banks: Record<string, {
    ticker: string
    current_price?: number
    price_change_pct?: number
    silver_exposure: {
      risk_level: string
      verification_status?: string
      claimed_short_position_tons?: number
      claimed_exposure_usd?: number
      source?: string
      source_author?: string
      concerns?: string[]
      action?: string
    }
    liquidity_risk?: {
      risk_level: string
      verification_status?: string
      unrealized_bond_losses?: number
    }
    overall_crisis_risk: string
    risk_note?: string
  }>
  unverified_claims_watchlist: Array<{
    id: string
    claim: string
    exposure_claimed?: string
    source: string
    source_type: string
    author?: string
    date_reported?: string
    verification_status: string
    credibility_concerns?: string[]
    debunked_by?: string[]
    notes?: string
    recommended_action: string
    status?: string
  }>
  historical_context: {
    bank_manipulation_settlements: {
      total_fines: number
      period_of_manipulation: string
      prosecution_period: string
      major_settlements: Array<{ bank: string; amount: number; year: number }>
      criminal_convictions: Array<{ name: string; role: string; sentence: string; year: number }>
      note: string
    }
  }
  next_scan_priorities: string[]
}

// Crisis Gauge Types
export interface CrackIndicator {
  id: string
  name: string
  description: string
  status: 'clear' | 'watching' | 'warning' | 'critical' | 'unknown'
  value: string | null
  threshold: string | null
  source: string | null
  source_url: string | null
}

export interface ExposureLoss {
  entity: string
  exposure_oz: number
  exposure_label: string
  loss_per_dollar: number
  total_loss: number
  loss_label: string
  market_cap: number | null
  loss_vs_cap_pct: number | null
  is_verified: boolean
}

export interface PhaseIndicator {
  id: string
  description: string
  status: boolean
  source: string | null
}

export interface CrisisPhase {
  phase: number
  name: string
  description: string
  indicators: PhaseIndicator[]
  progress_pct: number
}

export interface CrisisGaugeData {
  silver_price: number
  silver_base_price: number
  silver_move: number
  losses: ExposureLoss[]
  total_aggregate_loss: number
  tier1_cracks: CrackIndicator[]
  tier2_cracks: CrackIndicator[]
  tier3_cracks: CrackIndicator[]
  phases: CrisisPhase[]
  current_phase: number
  cracks_showing_count: number
  total_cracks: number
  crisis_probability: number
  crisis_level: string
  crisis_color: string
  resources: Array<{ name: string; tracks: string; url: string }>
}
