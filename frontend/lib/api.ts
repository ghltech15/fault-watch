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

export interface AlertData {
  level: 'critical' | 'warning' | 'info'
  title: string
  detail: string
  action?: string
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
  position: 'SHORT' | 'LONG' | 'NATIONALIZED'
  ounces: number
  equity: number
  insolvency_price: number | null
  deadline: string | null
  regulator: string | null
  loss_ratio_at_80: number | null
  note: string | null
  nationalization_date: string | null
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
  ubs_nationalized: boolean
  ubs_nationalization_date: string
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

export const api = {
  getDashboard: () => fetchAPI<DashboardData>('/api/dashboard'),
  getPrices: () => fetchAPI<Record<string, PriceData>>('/api/prices'),
  getCountdowns: () => fetchAPI<Record<string, CountdownData>>('/api/countdowns'),
  getAlerts: () => fetchAPI<AlertData[]>('/api/alerts'),
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
}
