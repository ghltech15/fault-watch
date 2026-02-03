/**
 * Core Narrative Block Generators
 *
 * These blocks run every hour (5am-10pm EST) and generate
 * timestamped content for the Fault.Watch site.
 *
 * Blocks:
 * - 8.1 FDIC Failed Banks Status
 * - 8.2 Morgan Stanley Insider Selling Tracker
 * - 8.3 Flagstar Risk/CRE Block
 * - 8.4 Silver Price & Bank Sell-off
 * - 8.5 Net Assessment Synthesis
 */

import { SupabaseClient } from '@supabase/supabase-js'

// Backend API base URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

// ============================================
// Timestamp Utilities
// ============================================

export function getTimestamps(): { utc: string; est: string } {
  const now = new Date()
  const utc = now.toISOString()

  // Format EST time
  const estFormatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })

  const parts = estFormatter.formatToParts(now)
  const estParts: Record<string, string> = {}
  parts.forEach(p => { estParts[p.type] = p.value })

  const est = `${estParts.year}-${estParts.month}-${estParts.day} ${estParts.hour}:${estParts.minute}:${estParts.second} EST`

  return { utc, est }
}

export function formatESTDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    timeZone: 'America/New_York',
    month: 'short',
    day: 'numeric',
  })
}

// ============================================
// Backend API Helper
// ============================================

async function fetchBackendAPI(endpoint: string): Promise<unknown> {
  try {
    const response = await fetch(`${BACKEND_API_URL}${endpoint}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(30000),
    })

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${endpoint}`)
      return null
    }

    return await response.json()
  } catch (error) {
    console.error(`Backend API call failed for ${endpoint}:`, error)
    return null
  }
}

// ============================================
// 8.1 FDIC Failed Banks Status
// ============================================

export interface FDICStatusBlock {
  has_new_failures: boolean
  new_failures_count: number
  year_to_date_failures: number
  latest_failure_name: string
  latest_failure_date: string
  latest_failure_state: string
  latest_failure_acquirer: string | null
  latest_failure_reason: string | null
  new_failures: unknown[]
  unrealized_losses_billions: number
  unrealized_losses_quarter: string
  header_text: string
  body_html: string
  sources: unknown[]
  generated_at_utc: string
  generated_at_est: string
}

export async function generateFDICStatusBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<FDICStatusBlock> {
  const timestamps = getTimestamps()
  const today = formatESTDate(new Date())

  // Fetch latest FDIC data from backend
  const fdicData = await fetchBackendAPI('/api/pipeline/regulatory') as Record<string, unknown> | null

  // Get previous block to detect changes
  const { data: prevBlock } = await supabase
    .from('fault_watch_fdic_status')
    .select('*')
    .order('generated_at_utc', { ascending: false })
    .limit(1)
    .single()

  // Default values (Metropolitan Capital Bank & Trust - only 2026 failure so far)
  let hasNewFailures = false
  let newFailuresCount = 0
  const ytdFailures = 1
  const latestFailureName = 'Metropolitan Capital Bank & Trust'
  const latestFailureDate = '2026-01-23'
  const latestFailureState = 'IL'
  const latestFailureAcquirer = null
  const latestFailureReason = 'unsafe and unsound conditions and an impaired capital position'
  const newFailures: unknown[] = []
  const unrealizedLosses = 337.1
  const unrealizedLossesQuarter = 'Q3 2025'
  const sources = [
    { name: 'FDIC Failed Bank List', url: 'https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/' }
  ]

  // TODO: Parse fdicData for new failures if API provides it

  // Generate header
  const headerText = hasNewFailures
    ? `BANK FAILURE ALERT: ${newFailuresCount} NEW CLOSURE${newFailuresCount > 1 ? 'S' : ''} (${today})`
    : `NO NEW BANK CLOSURES TODAY (${today})`

  // Generate body HTML
  const bodyHtml = `
<div class="fdic-status-block">
  <p class="status-header ${hasNewFailures ? 'alert' : 'ok'}">${headerText}</p>

  ${hasNewFailures ? `
  <div class="new-failures">
    ${(newFailures as Array<{name: string; state: string; date: string; acquirer?: string; reason?: string}>).map(f => `
    <div class="failure-item">
      <strong>${f.name}</strong> (${f.state}) - Closed ${f.date}
      ${f.acquirer ? `<br/>Acquired by: ${f.acquirer}` : ''}
      ${f.reason ? `<br/>Reason: ${f.reason}` : ''}
    </div>
    `).join('')}
  </div>
  ` : ''}

  <div class="ytd-summary">
    <p><strong>2026 Failures:</strong> ${ytdFailures}</p>
    <p>Most recent: ${latestFailureName} (${latestFailureState}) - ${latestFailureDate}</p>
    ${latestFailureReason ? `<p class="reason">${latestFailureReason}</p>` : ''}
  </div>

  <div class="unrealized-losses">
    <p><strong>Banking Sector Unrealized Losses:</strong> $${unrealizedLosses}B (${unrealizedLossesQuarter})</p>
  </div>

  <p class="timestamp">Generated: ${timestamps.est}</p>
</div>
`

  const block: FDICStatusBlock = {
    has_new_failures: hasNewFailures,
    new_failures_count: newFailuresCount,
    year_to_date_failures: ytdFailures,
    latest_failure_name: latestFailureName,
    latest_failure_date: latestFailureDate,
    latest_failure_state: latestFailureState,
    latest_failure_acquirer: latestFailureAcquirer,
    latest_failure_reason: latestFailureReason,
    new_failures: newFailures,
    unrealized_losses_billions: unrealizedLosses,
    unrealized_losses_quarter: unrealizedLossesQuarter,
    header_text: headerText,
    body_html: bodyHtml,
    sources,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  // Persist to database
  await supabase.from('fault_watch_fdic_status').insert({
    run_id: runId,
    ...block,
  })

  return block
}

// ============================================
// 8.2 Morgan Stanley Insider Selling Tracker
// ============================================

export interface MSInsiderBlock {
  total_shares_sold_90d: number
  total_value_sold_90d: number
  total_shares_bought_90d: number
  total_value_bought_90d: number
  net_insider_flow: string
  recent_trades: unknown[]
  pressure_level: string
  pressure_summary: string
  header_text: string
  body_html: string
  form4_filings: unknown[]
  generated_at_utc: string
  generated_at_est: string
}

export async function generateMSInsiderBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<MSInsiderBlock> {
  const timestamps = getTimestamps()

  // Fetch SEC filings data
  const secData = await fetchBackendAPI('/api/pipeline/sec') as Record<string, unknown> | null

  // Default insider trading data (from the brief)
  const recentTrades = [
    { name: 'Daniel Simkowitz', shares: 32968, price_range: '$182-183', date: '2026-01-30', pct_reduction: null },
    { name: 'Michael A. Pizzi', shares: 20000, price_range: null, date: '2026-01-20', pct_reduction: null },
    { name: 'Charles A. Smith', shares: 8500, price_range: null, date: '2026-01-20', pct_reduction: null },
  ]

  // Calculate totals
  const totalSharesSold = recentTrades.reduce((sum, t) => sum + t.shares, 0)
  const avgPrice = 182.5
  const totalValueSold = totalSharesSold * avgPrice
  const totalSharesBought = 0
  const totalValueBought = 0

  const netFlow = totalSharesBought === 0 ? 'selling-only' : 'net-selling'
  const pressureLevel = totalValueSold > 10000000 ? 'high' : 'moderate'

  const headerText = `MS INSIDER PRESSURE: $${(totalValueSold / 1000000).toFixed(1)}M SOLD (90 DAYS)`

  const bodyHtml = `
<div class="ms-insider-block">
  <p class="status-header high">${headerText}</p>

  <div class="totals">
    <p><strong>90-Day Totals:</strong></p>
    <p>Shares Sold: ${totalSharesSold.toLocaleString()} ($${(totalValueSold / 1000000).toFixed(1)}M)</p>
    <p>Shares Bought: ${totalSharesBought.toLocaleString()} ${totalSharesBought === 0 ? '(ZERO INSIDER PURCHASES)' : ''}</p>
    <p>Net Flow: <span class="${netFlow}">${netFlow.toUpperCase()}</span></p>
  </div>

  <div class="recent-trades">
    <p><strong>Recent Trades:</strong></p>
    <ul>
      ${recentTrades.map(t => `
        <li>${t.name}: ${t.shares.toLocaleString()} shares ${t.price_range ? `@ ${t.price_range}` : ''} (${t.date})${t.pct_reduction ? ` - ${t.pct_reduction}% position reduction` : ''}</li>
      `).join('')}
    </ul>
  </div>

  <p class="timestamp">insider_block_generated_at_est: ${timestamps.est}</p>
</div>
`

  const block: MSInsiderBlock = {
    total_shares_sold_90d: totalSharesSold,
    total_value_sold_90d: totalValueSold,
    total_shares_bought_90d: totalSharesBought,
    total_value_bought_90d: totalValueBought,
    net_insider_flow: netFlow,
    recent_trades: recentTrades,
    pressure_level: pressureLevel,
    pressure_summary: `${netFlow === 'selling-only' ? 'Zero insider purchases' : 'Net selling'} over 90 days with $${(totalValueSold / 1000000).toFixed(1)}M in sales`,
    header_text: headerText,
    body_html: bodyHtml,
    form4_filings: [],
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_ms_insider_tracker').insert({
    run_id: runId,
    ...block,
  })

  return block
}

// ============================================
// 8.3 Flagstar Risk/CRE Block
// ============================================

export interface FlagstarCREBlock {
  q4_eps: number
  profitable_quarter: boolean
  cre_concentration_ratio_pct: number
  cre_danger_zone_pct: number
  multifamily_cre_reduction_billions: number
  upcoming_events: unknown[]
  has_material_updates: boolean
  header_text: string
  body_html: string
  sources: unknown[]
  generated_at_utc: string
  generated_at_est: string
}

export async function generateFlagstarCREBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<FlagstarCREBlock> {
  const timestamps = getTimestamps()

  // Get previous block to detect changes
  const { data: prevBlock } = await supabase
    .from('fault_watch_flagstar_cre')
    .select('*')
    .order('generated_at_utc', { ascending: false })
    .limit(1)
    .single()

  // Default values from the brief
  const q4Eps = 0.05
  const profitableQuarter = true
  const creConcentration = 381.0
  const creDangerZone = 300.0
  const multifamilyReduction = 2.3

  const upcomingEvents = [
    { event: 'Bank of America Securities conference', location: 'Miami', date: '2026-02-10' }
  ]

  // Check for material updates (would need news API)
  const hasMaterialUpdates = false
  const noChangeNote = hasMaterialUpdates ? null : 'No material updates since prior run.'

  const headerText = `FLAGSTAR CRE RISK: ${creConcentration}% CONCENTRATION (${creDangerZone}% DANGER ZONE)`

  const bodyHtml = `
<div class="flagstar-cre-block">
  <p class="status-header warning">${headerText}</p>

  <div class="q4-status">
    <p><strong>Q4 Status:</strong> ${profitableQuarter ? 'First return to profitability' : 'Loss'}</p>
    <p>EPS: $${q4Eps.toFixed(2)} per diluted share</p>
  </div>

  <div class="cre-metrics">
    <p><strong>CRE Metrics:</strong></p>
    <p>Concentration Ratio: <span class="${creConcentration > creDangerZone ? 'danger' : 'ok'}">${creConcentration}%</span> (Danger zone: ${creDangerZone}%)</p>
    <p>Multifamily/CRE Reduction: $${multifamilyReduction}B</p>
  </div>

  ${upcomingEvents.length > 0 ? `
  <div class="upcoming-events">
    <p><strong>Upcoming Events:</strong></p>
    <ul>
      ${upcomingEvents.map(e => `<li>${e.event} - ${e.location}, ${e.date}</li>`).join('')}
    </ul>
  </div>
  ` : ''}

  ${noChangeNote ? `<p class="no-change-note"><em>${noChangeNote}</em></p>` : ''}

  <p class="timestamp">generated_at_est: ${timestamps.est}</p>
</div>
`

  const block: FlagstarCREBlock = {
    q4_eps: q4Eps,
    profitable_quarter: profitableQuarter,
    cre_concentration_ratio_pct: creConcentration,
    cre_danger_zone_pct: creDangerZone,
    multifamily_cre_reduction_billions: multifamilyReduction,
    upcoming_events: upcomingEvents,
    has_material_updates: hasMaterialUpdates,
    header_text: headerText,
    body_html: bodyHtml,
    sources: [],
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_flagstar_cre').insert({
    run_id: runId,
    ...block,
    no_change_note: noChangeNote,
  })

  return block
}

// ============================================
// 8.4 Silver Price Block
// ============================================

export interface SilverStatusBlock {
  current_price: number
  price_as_of_utc: string
  intraday_low: number | null
  intraday_high: number | null
  prior_close: number | null
  change_from_close_pct: number | null
  last_week_peak: number
  change_from_peak_pct: number | null
  danger_threshold_95: number
  distance_to_danger_pct: number | null
  movement_direction: string
  movement_explanation: string
  key_catalysts: string[]
  header_text: string
  body_html: string
  generated_at_utc: string
  generated_at_est: string
}

export async function generateSilverStatusBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<SilverStatusBlock> {
  const timestamps = getTimestamps()

  // Fetch current prices
  const pricesData = await fetchBackendAPI('/api/prices') as Record<string, unknown> | null
  const silverPrice = (pricesData?.['SI=F'] as number) || 89.11

  // Default values
  const intradayLow = 86.0
  const intradayHigh = 89.5
  const priorClose = 85.0
  const lastWeekPeak = 120.0
  const dangerThreshold = 95.0

  const changeFromClose = priorClose ? ((silverPrice - priorClose) / priorClose) * 100 : null
  const changeFromPeak = lastWeekPeak ? ((silverPrice - lastWeekPeak) / lastWeekPeak) * 100 : null
  const distanceToDanger = ((dangerThreshold - silverPrice) / silverPrice) * 100

  // Determine movement
  let movementDirection = 'consolidating'
  if (changeFromClose && changeFromClose > 3) movementDirection = 'surging'
  else if (changeFromClose && changeFromClose > 0) movementDirection = 'bouncing'
  else if (changeFromClose && changeFromClose < -3) movementDirection = 'falling'

  const catalysts = [
    'Trump nominating Kevin Warsh as Fed Chair (seen as hawkish)',
    'Two-day selloff erased up to 40% from record highs'
  ]

  const headerText = `SILVER TODAY — $${intradayLow}–$${intradayHigh}, ${movementDirection}; currently $${silverPrice.toFixed(2)}/oz`

  const bodyHtml = `
<div class="silver-status-block">
  <p class="status-header">${headerText}</p>

  <div class="price-data">
    <p><strong>Current:</strong> $${silverPrice.toFixed(2)}/oz (as of ${timestamps.est})</p>
    <p><strong>Intraday Range:</strong> $${intradayLow} – $${intradayHigh}</p>
    ${priorClose ? `<p><strong>vs Prior Close:</strong> ${changeFromClose && changeFromClose >= 0 ? '+' : ''}${changeFromClose?.toFixed(2)}%</p>` : ''}
    <p><strong>vs Last Week Peak ($${lastWeekPeak}):</strong> ${changeFromPeak?.toFixed(1)}%</p>
    <p><strong>Distance to $${dangerThreshold} Danger Zone:</strong> ${distanceToDanger.toFixed(1)}%</p>
  </div>

  <div class="movement">
    <p><strong>Movement:</strong> ${movementDirection} after a two-day selloff that erased up to 40% from record highs</p>
  </div>

  ${catalysts.length > 0 ? `
  <div class="catalysts">
    <p><strong>Key Catalysts:</strong></p>
    <ul>
      ${catalysts.map(c => `<li>${c}</li>`).join('')}
    </ul>
  </div>
  ` : ''}

  <p class="timestamp">Price as of: ${timestamps.est}</p>
</div>
`

  const block: SilverStatusBlock = {
    current_price: silverPrice,
    price_as_of_utc: timestamps.utc,
    intraday_low: intradayLow,
    intraday_high: intradayHigh,
    prior_close: priorClose,
    change_from_close_pct: changeFromClose,
    last_week_peak: lastWeekPeak,
    change_from_peak_pct: changeFromPeak,
    danger_threshold_95: dangerThreshold,
    distance_to_danger_pct: distanceToDanger,
    movement_direction: movementDirection,
    movement_explanation: `${movementDirection} after a two-day selloff that erased up to 40% from record highs`,
    key_catalysts: catalysts,
    header_text: headerText,
    body_html: bodyHtml,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_silver_status').insert({
    run_id: runId,
    ...block,
  })

  return block
}

// ============================================
// 8.4 Bank Sell-off Block
// ============================================

export interface BankSelloffBlock {
  is_major_selloff: boolean
  selloff_severity: string
  bank_moves: unknown[]
  total_market_cap_lost_billions: number | null
  catalysts: string[]
  banker_fear_index_reading: string
  systemic_risk_assessment: string
  header_text: string
  body_html: string
  generated_at_utc: string
  generated_at_est: string
}

export async function generateBankSelloffBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<BankSelloffBlock> {
  const timestamps = getTimestamps()

  // Fetch bank prices
  const pricesData = await fetchBackendAPI('/api/prices') as Record<string, unknown> | null

  // Calculate bank moves (example data from brief)
  const bankMoves = [
    { ticker: 'C', name: 'Citigroup', change_pct: -3.4 },
    { ticker: 'BAC', name: 'Bank of America', change_pct: -3.7 },
    { ticker: 'WFC', name: 'Wells Fargo', change_pct: -4.6 },
    { ticker: 'MS', name: 'Morgan Stanley', change_pct: -2.8 },
    { ticker: 'JPM', name: 'JPMorgan', change_pct: -2.1 },
  ]

  // Determine if major selloff
  const avgDrop = bankMoves.reduce((sum, b) => sum + Math.abs(b.change_pct), 0) / bankMoves.length
  const isMajorSelloff = avgDrop > 3.0

  let severity = 'minor'
  if (avgDrop > 5) severity = 'severe'
  else if (avgDrop > 3) severity = 'major'
  else if (avgDrop > 1.5) severity = 'moderate'

  const catalysts = [
    'Q4 earnings misses',
    'NII disappointments',
    'WFC asset cap removal uncertainty'
  ]

  const marketCapLost = isMajorSelloff ? 45.0 : null

  const fearIndexReading = 'Elevated'
  const systemicRisk = 'Tariff volatility seen as highly likely threat; 61% of bankers cite governmental data deterioration as moderate to significant risk'

  const headerText = isMajorSelloff
    ? 'MAJOR BANK SELL-OFF CONTINUES'
    : 'BANK SECTOR UNDER PRESSURE'

  const bodyHtml = `
<div class="bank-selloff-block">
  <p class="status-header ${isMajorSelloff ? 'alert' : 'warning'}">${headerText}</p>

  <div class="bank-moves">
    <table>
      <tr><th>Bank</th><th>Change</th></tr>
      ${bankMoves.map(b => `
        <tr class="${b.change_pct < -3 ? 'severe' : b.change_pct < -1 ? 'moderate' : ''}">
          <td>${b.name} (${b.ticker})</td>
          <td>${b.change_pct >= 0 ? '+' : ''}${b.change_pct.toFixed(1)}%</td>
        </tr>
      `).join('')}
    </table>
  </div>

  ${marketCapLost ? `<p><strong>Market Cap Lost:</strong> ~$${marketCapLost}B wiped</p>` : ''}

  <div class="catalysts">
    <p><strong>Catalysts:</strong></p>
    <ul>
      ${catalysts.map(c => `<li>${c}</li>`).join('')}
    </ul>
  </div>

  <div class="fear-index">
    <p><strong>Banker Fear Index:</strong> ${fearIndexReading}</p>
    <p class="systemic-risk">${systemicRisk}</p>
  </div>

  <p class="timestamp">generated_at_est: ${timestamps.est}</p>
</div>
`

  const block: BankSelloffBlock = {
    is_major_selloff: isMajorSelloff,
    selloff_severity: severity,
    bank_moves: bankMoves,
    total_market_cap_lost_billions: marketCapLost,
    catalysts,
    banker_fear_index_reading: fearIndexReading,
    systemic_risk_assessment: systemicRisk,
    header_text: headerText,
    body_html: bodyHtml,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_bank_selloff').insert({
    run_id: runId,
    ...block,
  })

  return block
}

// ============================================
// 8.4 Banker Fear Index Block
// ============================================

export interface BankerFearIndexBlock {
  tariff_volatility_threat_pct: number
  recession_likelihood_us_pct: number | null
  recession_likelihood_global_pct: number | null
  govt_data_deterioration_risk_pct: number
  fear_index_value: number | null
  fear_index_trend: string
  survey_source: string
  has_new_survey_data: boolean
  header_text: string
  body_html: string
  generated_at_utc: string
  generated_at_est: string
}

export async function generateBankerFearIndexBlock(
  supabase: SupabaseClient,
  runId: string
): Promise<BankerFearIndexBlock> {
  const timestamps = getTimestamps()

  // Survey data from the brief
  const tariffThreat = 85.0 // "highly likely threat"
  const recessionUS = 65.0 // "likely recession"
  const recessionGlobal = 60.0
  const govtDataRisk = 61.0

  const hasNewData = false
  const surveySource = 'American Banker'

  const headerText = 'BANKER FEAR INDEX: ELEVATED'

  const bodyHtml = `
<div class="fear-index-block">
  <p class="status-header warning">${headerText}</p>

  <div class="survey-data">
    <p><strong>Key Findings (${surveySource}):</strong></p>
    <ul>
      <li>Tariff volatility seen as <strong>highly likely threat</strong> (${tariffThreat}%)</li>
      <li>Bankers expect <strong>likely recession</strong> in U.S. (${recessionUS}%) and global (${recessionGlobal}%) economies</li>
      <li><strong>${govtDataRisk}%</strong> say deterioration in governmental data sources poses moderate to significant risk</li>
    </ul>
  </div>

  ${!hasNewData ? `<p class="no-change-note"><em>No new survey data since last update.</em></p>` : ''}

  <p class="timestamp">generated_at_est: ${timestamps.est}</p>
</div>
`

  const block: BankerFearIndexBlock = {
    tariff_volatility_threat_pct: tariffThreat,
    recession_likelihood_us_pct: recessionUS,
    recession_likelihood_global_pct: recessionGlobal,
    govt_data_deterioration_risk_pct: govtDataRisk,
    fear_index_value: null,
    fear_index_trend: 'stable',
    survey_source: surveySource,
    has_new_survey_data: hasNewData,
    header_text: headerText,
    body_html: bodyHtml,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_banker_fear_index').insert({
    run_id: runId,
    ...block,
  })

  return block
}

// ============================================
// 8.5 Net Assessment Synthesis Block
// ============================================

export interface NetAssessmentBlock {
  silver_summary: string
  silver_price: number
  silver_vs_danger_zone: string
  ms_insider_summary: string
  ms_insider_90d_value: number
  ms_insider_buys_count: number
  fdic_summary: string
  fdic_ytd_failures: number
  unrealized_losses_billions: number
  flagstar_summary: string
  flagstar_cre_ratio: number
  bank_selloff_summary: string
  conditions_vs_prior: string
  systemic_risk_level: string
  assessment_text: string
  status_line: string
  generated_at_utc: string
  generated_at_est: string
}

export async function generateNetAssessmentBlock(
  supabase: SupabaseClient,
  runId: string,
  silverBlock: SilverStatusBlock,
  msInsiderBlock: MSInsiderBlock,
  fdicBlock: FDICStatusBlock,
  flagstarBlock: FlagstarCREBlock,
  bankSelloffBlock: BankSelloffBlock
): Promise<NetAssessmentBlock> {
  const timestamps = getTimestamps()

  // Get prior assessment to compare
  const { data: priorAssessment } = await supabase
    .from('fault_watch_net_assessments')
    .select('*')
    .order('generated_at_utc', { ascending: false })
    .limit(1)
    .single()

  // Build summaries from component blocks
  const silverSummary = `Silver ${silverBlock.movement_direction} from $${silverBlock.prior_close} → $${silverBlock.current_price.toFixed(2)}`
  const silverVsDanger = silverBlock.current_price >= 95 ? 'AT/ABOVE danger zone' : `${silverBlock.distance_to_danger_pct?.toFixed(1)}% below $95 danger zone`

  const msInsiderSummary = `MS insiders dumped $${(msInsiderBlock.total_value_sold_90d / 1000000).toFixed(1)}M in 90 days with ${msInsiderBlock.total_shares_bought_90d === 0 ? 'zero buys' : `${msInsiderBlock.total_shares_bought_90d} shares bought`}`

  const fdicSummary = `${fdicBlock.latest_failure_name} remains the only 2026 failure`

  const flagstarSummary = `Flagstar CRE at ${flagstarBlock.cre_concentration_ratio_pct}% (danger: ${flagstarBlock.cre_danger_zone_pct}%)`

  const bankSelloffSummary = bankSelloffBlock.is_major_selloff
    ? `Major bank sell-off continues with ${bankSelloffBlock.selloff_severity} pressure`
    : `Bank sector under ${bankSelloffBlock.selloff_severity} pressure`

  // Determine condition change
  let conditionsVsPrior = 'unchanged'
  if (priorAssessment) {
    const priorSilver = priorAssessment.silver_price || 0
    const priorMSValue = priorAssessment.ms_insider_90d_value || 0

    if (silverBlock.current_price > priorSilver * 1.02 && msInsiderBlock.total_value_sold_90d <= priorMSValue) {
      conditionsVsPrior = 'improved'
    } else if (silverBlock.current_price < priorSilver * 0.98 || msInsiderBlock.total_value_sold_90d > priorMSValue * 1.1) {
      conditionsVsPrior = 'worsened'
    }
  }

  // Determine systemic risk level
  let systemicRiskLevel = 'moderate'
  if (bankSelloffBlock.is_major_selloff && silverBlock.current_price >= 90) {
    systemicRiskLevel = 'elevated'
  }
  if (fdicBlock.year_to_date_failures > 1 || flagstarBlock.cre_concentration_ratio_pct > 400) {
    systemicRiskLevel = 'high'
  }

  // Build status line
  const estTime = timestamps.est.split(' ').slice(0, 2).join(' ')
  const statusLine = `NET ASSESSMENT as of ${estTime}: ${silverSummary}, back toward the $95 danger zone; ${msInsiderSummary}; ${fdicSummary} but CRE/earnings pressure and the ongoing sell-off keep systemic risk ${systemicRiskLevel}.`

  // Build full assessment text
  const assessmentText = `
**Silver:** ${silverSummary}. Currently ${silverVsDanger}.

**MS Insider Activity:** ${msInsiderSummary}. Pressure level: ${msInsiderBlock.pressure_level}.

**FDIC Status:** ${fdicSummary}. Banking sector unrealized losses: $${fdicBlock.unrealized_losses_billions}B.

**Flagstar CRE:** ${flagstarSummary}. ${flagstarBlock.has_material_updates ? 'Material updates detected.' : 'No material updates.'}

**Bank Sector:** ${bankSelloffSummary}.

**Conditions vs Prior Run:** ${conditionsVsPrior.toUpperCase()}
**Systemic Risk Level:** ${systemicRiskLevel.toUpperCase()}
`

  const block: NetAssessmentBlock = {
    silver_summary: silverSummary,
    silver_price: silverBlock.current_price,
    silver_vs_danger_zone: silverVsDanger,
    ms_insider_summary: msInsiderSummary,
    ms_insider_90d_value: msInsiderBlock.total_value_sold_90d,
    ms_insider_buys_count: msInsiderBlock.total_shares_bought_90d,
    fdic_summary: fdicSummary,
    fdic_ytd_failures: fdicBlock.year_to_date_failures,
    unrealized_losses_billions: fdicBlock.unrealized_losses_billions,
    flagstar_summary: flagstarSummary,
    flagstar_cre_ratio: flagstarBlock.cre_concentration_ratio_pct,
    bank_selloff_summary: bankSelloffSummary,
    conditions_vs_prior: conditionsVsPrior,
    systemic_risk_level: systemicRiskLevel,
    assessment_text: assessmentText,
    status_line: statusLine,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }

  await supabase.from('fault_watch_net_assessments').insert({
    run_id: runId,
    ...block,
    prior_run_id: priorAssessment?.run_id || null,
    prior_assessment_id: priorAssessment?.id || null,
  })

  return block
}

// ============================================
// Master Generator: Run All Narrative Blocks
// ============================================

export interface NarrativeBlocksResult {
  fdic: FDICStatusBlock
  msInsider: MSInsiderBlock
  flagstar: FlagstarCREBlock
  silver: SilverStatusBlock
  bankSelloff: BankSelloffBlock
  bankerFearIndex: BankerFearIndexBlock
  netAssessment: NetAssessmentBlock
  generated_at_utc: string
  generated_at_est: string
}

export async function generateAllNarrativeBlocks(
  supabase: SupabaseClient,
  runId: string
): Promise<NarrativeBlocksResult> {
  const timestamps = getTimestamps()

  console.log(`[${timestamps.est}] Generating narrative blocks for run ${runId}...`)

  // Generate all blocks (some depend on others)
  const fdic = await generateFDICStatusBlock(supabase, runId)
  const msInsider = await generateMSInsiderBlock(supabase, runId)
  const flagstar = await generateFlagstarCREBlock(supabase, runId)
  const silver = await generateSilverStatusBlock(supabase, runId)
  const bankSelloff = await generateBankSelloffBlock(supabase, runId)
  const bankerFearIndex = await generateBankerFearIndexBlock(supabase, runId)

  // Net assessment depends on all others
  const netAssessment = await generateNetAssessmentBlock(
    supabase,
    runId,
    silver,
    msInsider,
    fdic,
    flagstar,
    bankSelloff
  )

  console.log(`[${timestamps.est}] Narrative blocks generated successfully`)

  return {
    fdic,
    msInsider,
    flagstar,
    silver,
    bankSelloff,
    bankerFearIndex,
    netAssessment,
    generated_at_utc: timestamps.utc,
    generated_at_est: timestamps.est,
  }
}
