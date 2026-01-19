// Crisis Scanner Types
// Based on Fault Watch Crisis Scanner Module Specification v1.0

// ============================================
// Verification & Source Types
// ============================================

export type VerificationLevel = 'VERIFIED' | 'CREDIBLE' | 'UNVERIFIED' | 'SPECULATIVE'

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'ELEVATED' | 'MODERATE' | 'LOW' | 'UNKNOWN'

export type AlertLevelCode = 1 | 2 | 3 | 4 | 5

export type AlertLevel = 'CRITICAL' | 'HIGH' | 'ELEVATED' | 'MODERATE' | 'LOW'

export type PositionDirection = 'LONG' | 'SHORT' | 'UNKNOWN'

export type IndicatorStatus = 'ALERT' | 'WARNING' | 'NORMAL'

export type ClaimStatus = 'AWAITING_CORROBORATION' | 'MONITORING' | 'PARTIALLY_CORROBORATED' | 'EFFECTIVELY_DEBUNKED' | 'CONFIRMED'

// ============================================
// Alert Configuration
// ============================================

export interface AlertLevelConfig {
  color: string
  icon: string
  name: AlertLevel
  description: string
  triggers: string[]
  action: string
}

export const ALERT_LEVELS: Record<string, AlertLevelConfig> = {
  LEVEL_5_CRITICAL: {
    color: '#DC2626',
    icon: '5',
    name: 'CRITICAL',
    description: 'Immediate systemic risk - potential bank failure imminent',
    triggers: [
      'Fed emergency facility usage > $100B single day',
      'Trading halt on major bank stock',
      'Credit rating downgrade to junk',
      'Confirmed margin call failure',
      'FDIC intervention announced'
    ],
    action: 'IMMEDIATE REVIEW REQUIRED'
  },
  LEVEL_4_HIGH: {
    color: '#EA580C',
    icon: '4',
    name: 'HIGH',
    description: 'Significant stress indicators - elevated monitoring',
    triggers: [
      'Fed repo usage > $50B (non year-end)',
      'Silver backwardation > 5%',
      'COMEX registered inventory < 50M oz',
      'Bank stock drops > 10% single day',
      'Credible whistleblower report published'
    ],
    action: 'ENHANCED MONITORING'
  },
  LEVEL_3_ELEVATED: {
    color: '#F59E0B',
    icon: '3',
    name: 'ELEVATED',
    description: 'Stress indicators present - watch closely',
    triggers: [
      'Fed repo usage > $25B (non year-end)',
      'Silver in backwardation',
      'COMEX deliveries exceed 20M oz/month',
      'Margin requirements increased',
      'Unverified stress reports circulating'
    ],
    action: 'INCREASED VIGILANCE'
  },
  LEVEL_2_MODERATE: {
    color: '#10B981',
    icon: '2',
    name: 'MODERATE',
    description: 'Normal market conditions with some volatility',
    triggers: [
      'Standard Fed facility usage',
      'Silver in contango',
      'Normal COMEX delivery patterns'
    ],
    action: 'ROUTINE MONITORING'
  },
  LEVEL_1_LOW: {
    color: '#6B7280',
    icon: '1',
    name: 'LOW',
    description: 'Calm markets - no stress indicators',
    triggers: [],
    action: 'STANDARD OPERATIONS'
  }
}

// ============================================
// Silver Market Types
// ============================================

export interface PriceData {
  spot_price: number
  user_tracked_high: number
  user_tracked_low: number
  recovery_from_low_pct: number
  user_thesis: string
}

export interface MarketStructure {
  backwardation: boolean
  backwardation_status: string
  verification: VerificationLevel
  source: string
  significance: string
}

export interface ComexInventory {
  registered_oz: number
  registered_tons: number
  trend: 'DECLINING' | 'STABLE' | 'INCREASING'
  verification: VerificationLevel
  source: string
  as_of_date: string
}

export interface DeliveryActivity {
  date: string
  contracts_delivered: number
  ounces_delivered: number
  primary_issuer: string
  issuer_percentage: number
  verification: VerificationLevel
  source: string
  significance: string
}

export interface SupplyDeficit {
  year: number
  deficit_oz: number
  consecutive_deficit_years: number
  projected_2026_deficit_oz: number
  verification: VerificationLevel
  sources: string[]
}

export interface ExportCurbs {
  effective_date: string
  impact_description: string
  verification: VerificationLevel
  sources: string[]
}

export interface PhysicalPremiumReports {
  tokyo_premium_claimed: number
  dubai_premium_claimed: string
  verification: VerificationLevel
  note: string
}

export interface SilverMarket {
  price_data: PriceData
  market_structure: MarketStructure
  comex_inventory: ComexInventory
  delivery_activity: DeliveryActivity
  supply_deficit: SupplyDeficit
  china_export_curbs: ExportCurbs
  physical_premium_reports: PhysicalPremiumReports
}

// ============================================
// Federal Reserve Types
// ============================================

export interface RepoFacility {
  current_balance: number
  daily_limit: string | number
  limit_change_date: string
  previous_limit: number
  verification: VerificationLevel
  source: string
  significance: string
}

export interface YearEndSpike {
  date: string
  amount: number
  treasury_collateral: number
  mbs_collateral: number
  previous_record: number
  status: 'RESOLVED' | 'ACTIVE'
  resolution_date?: string
  verification: VerificationLevel
  source: string
  significance: string
}

export interface ReverseRepo {
  current_balance: number
  year_end_spike: number
  verification: VerificationLevel
  source: string
}

export interface QuantitativeTightening {
  status: 'ENDED' | 'ACTIVE'
  end_date?: string
  total_reduction: number
  verification: VerificationLevel
}

export interface FederalReserve {
  standing_repo_facility: RepoFacility
  year_end_spike: YearEndSpike
  reverse_repo: ReverseRepo
  quantitative_tightening: QuantitativeTightening
}

// ============================================
// Bank Risk Types
// ============================================

export interface SilverExposure {
  risk_level: RiskLevel
  verification_status?: VerificationLevel | 'UNKNOWN'
  claimed_short_position_tons?: number
  claimed_exposure_usd?: number
  source?: string
  source_author?: string
  concerns?: string[]
  notes?: string
  action?: string
  historical?: string
}

export interface LiquidityRisk {
  risk_level: RiskLevel
  verification_status?: VerificationLevel
  unrealized_bond_losses?: number
  source?: string
}

export interface WhistleblowerAllegation {
  status: string
  source: string
  claim: string
  alleged_timeframe: string
  raised_internally: string
  whistleblower_terminated: string
  document: string
  action: string
}

export interface Earnings {
  eps?: number
  eps_adjusted?: number
  eps_expected?: number
  revenue?: number
  nii_growth_pct?: number
  beat_estimates?: boolean
  ceo_warning?: string
  verification?: VerificationLevel
  source?: string
}

export interface WarningSignals {
  z_score: number
  z_score_meaning: string
  insider_selling_12mo: number
  source: string
}

export interface LoanLossProvisions {
  q1_2025?: number
  projected_increase?: string
  source?: string
  verification?: VerificationLevel
}

export interface StressTest {
  passed: boolean
  cet1_ratio: number
  minimum_required: number
  verification: VerificationLevel
}

export interface RegulatoryStatus {
  asset_cap_removed?: boolean
  removal_date?: string
  previous_cap?: number
  source?: string
  verification?: VerificationLevel
}

export interface ShadowBankExposure {
  percentage: number
  comparison: string
  source: string
  verification: VerificationLevel
}

export interface AnalystPosition {
  stance: string
  quote?: string
  entry_range?: string
  '2026_forecast_avg'?: number
  '2026_range'?: string
  '2026_target'?: number
  spike_possible?: number
  view?: string
  source: string
}

export interface BankProfile {
  ticker: string
  silver_exposure: SilverExposure
  liquidity_risk?: LiquidityRisk
  whistleblower_allegations?: WhistleblowerAllegation
  q4_2025_earnings?: Earnings
  warning_signals?: WarningSignals
  loan_loss_provisions?: LoanLossProvisions
  stress_test?: StressTest
  regulatory_status?: RegulatoryStatus
  shadow_bank_exposure?: ShadowBankExposure
  analyst_position?: AnalystPosition
  concerns?: { [key: string]: any }
  recent_developments?: { [key: string]: string }
  overall_crisis_risk: RiskLevel
  risk_note?: string
}

export interface Banks {
  jpmorgan_chase: BankProfile
  bank_of_america: BankProfile
  citigroup: BankProfile
  wells_fargo: BankProfile
  hsbc: BankProfile
  deutsche_bank: BankProfile
  ubs: BankProfile
  goldman_sachs: BankProfile
}

// ============================================
// Unverified Claims Types
// ============================================

export interface UnverifiedClaim {
  id: string
  claim: string
  exposure_claimed?: string
  source: string
  source_type: string
  author?: string
  date_reported?: string
  verification_status: VerificationLevel | ClaimStatus
  credibility_concerns?: string[]
  debunked_by?: string[]
  notes?: string
  recommended_action: string
  escalation_trigger?: string
  status?: string
}

// ============================================
// Historical Context Types
// ============================================

export interface Settlement {
  bank: string
  amount: number
  year: number
}

export interface CriminalConviction {
  name: string
  role: string
  sentence: string
  year: number
}

export interface ManipulationSettlements {
  total_fines: number
  period_of_manipulation: string
  prosecution_period: string
  major_settlements: Settlement[]
  criminal_convictions: CriminalConviction[]
  note: string
}

export interface HistoricalContext {
  bank_manipulation_settlements: ManipulationSettlements
}

// ============================================
// Scan Metadata & System Status
// ============================================

export interface ScanMetadata {
  scan_id: string
  scan_date: string
  scan_timestamp: string
  analyst: string
  version: string
}

export interface SystemStatus {
  alert_level: AlertLevel
  alert_level_code: AlertLevelCode
  primary_drivers: string[]
  recommended_action: string
}

// ============================================
// Main Scan Data Type
// ============================================

export interface CrisisScanData {
  scan_metadata: ScanMetadata
  system_status: SystemStatus
  silver_market: SilverMarket
  federal_reserve: FederalReserve
  banks: Banks
  unverified_claims_watchlist: UnverifiedClaim[]
  historical_context: HistoricalContext
  next_scan_priorities: string[]
}

// ============================================
// Component Props Types
// ============================================

export interface SilverIndicatorsProps {
  silver: SilverMarket
}

export interface FedFacilitiesProps {
  fed: FederalReserve
}

export interface BankRiskMatrixProps {
  banks: Banks
}

export interface AlertPanelProps {
  systemStatus: SystemStatus
  lastScan: string
}

export interface UnverifiedTrackerProps {
  claims: UnverifiedClaim[]
}

// ============================================
// Utility Functions
// ============================================

export function getAlertColor(level: AlertLevel): string {
  const colors: Record<AlertLevel, string> = {
    CRITICAL: '#DC2626',
    HIGH: '#EA580C',
    ELEVATED: '#F59E0B',
    MODERATE: '#10B981',
    LOW: '#6B7280'
  }
  return colors[level] || '#6B7280'
}

export function getRiskColor(level: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    CRITICAL: '#DC2626',
    HIGH: '#EA580C',
    ELEVATED: '#F59E0B',
    MODERATE: '#10B981',
    LOW: '#6B7280',
    UNKNOWN: '#9CA3AF'
  }
  return colors[level] || '#9CA3AF'
}

export function getVerificationColor(level: VerificationLevel): string {
  const colors: Record<VerificationLevel, string> = {
    VERIFIED: '#10B981',
    CREDIBLE: '#F59E0B',
    UNVERIFIED: '#EA580C',
    SPECULATIVE: '#DC2626'
  }
  return colors[level] || '#9CA3AF'
}

export function formatLargeNumber(num: number): string {
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`
  if (num >= 1e3) return `$${(num / 1e3).toFixed(1)}K`
  return `$${num.toFixed(2)}`
}

export function formatOunces(oz: number): string {
  if (oz >= 1e9) return `${(oz / 1e9).toFixed(2)}B oz`
  if (oz >= 1e6) return `${(oz / 1e6).toFixed(1)}M oz`
  if (oz >= 1e3) return `${(oz / 1e3).toFixed(1)}K oz`
  return `${oz.toFixed(0)} oz`
}
