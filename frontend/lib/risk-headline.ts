// Risk headline generation logic for fault.watch

import type { DashboardData, CrisisGaugeData } from './api'

export interface RiskHeadline {
  headline: string
  direction: 'rising' | 'falling' | 'stable'
  severity: 'low' | 'moderate' | 'elevated' | 'high' | 'critical'
  timestamp: Date
}

export interface RiskScanResult {
  timestamp: Date
  changes: {
    silverChange: number
    phaseChange: number
    cracksChange: number
  }
  thresholdCrossings: string[]
  headline: RiskHeadline
}

/**
 * Generate a daily risk headline from current dashboard data
 */
export function generateDailyHeadline(
  dashboard: DashboardData,
  crisisGauge?: CrisisGaugeData | null
): RiskHeadline {
  const silverChange = dashboard.prices?.silver?.change_pct || 0
  const silverPrice = dashboard.prices?.silver?.price || 0
  const phase = crisisGauge?.current_phase || 2
  const cracksShowing = crisisGauge?.cracks_showing_count || 0
  const totalCracks = crisisGauge?.total_cracks || 12
  const crisisProbability = crisisGauge?.crisis_probability || 0

  // Determine direction
  let direction: 'rising' | 'falling' | 'stable'
  if (silverChange > 1 || cracksShowing > 4) {
    direction = 'rising'
  } else if (silverChange < -1 && cracksShowing <= 2) {
    direction = 'falling'
  } else {
    direction = 'stable'
  }

  // Determine severity
  let severity: 'low' | 'moderate' | 'elevated' | 'high' | 'critical'
  if (phase >= 5 || crisisProbability >= 80) {
    severity = 'critical'
  } else if (phase >= 4 || crisisProbability >= 60) {
    severity = 'high'
  } else if (phase >= 3 || crisisProbability >= 40) {
    severity = 'elevated'
  } else if (cracksShowing >= 3 || crisisProbability >= 20) {
    severity = 'moderate'
  } else {
    severity = 'low'
  }

  // Build headline text
  const silverText = silverChange > 0
    ? `silver up ${silverChange.toFixed(1)}%`
    : silverChange < 0
    ? `silver down ${Math.abs(silverChange).toFixed(1)}%`
    : 'silver flat'

  const cracksText = cracksShowing > 0
    ? `${cracksShowing} indicator${cracksShowing > 1 ? 's' : ''} at Stressed`
    : 'all indicators stable'

  // Add notable events
  const events: string[] = []
  if (silverPrice >= 100) events.push('$100 threshold breached')
  else if (silverPrice >= 75) events.push('nearing stress zone')

  if (phase >= 4) events.push('cascade phase critical')
  else if (phase >= 3) events.push('cascade advancing')

  const eventText = events.length > 0 ? `, ${events.join(', ')}` : ''

  const headline = `Today: risk ${direction} – ${silverText}, ${cracksText}${eventText}`

  return {
    headline,
    direction,
    severity,
    timestamp: new Date()
  }
}

/**
 * Generate a shareable summary for the daily scan
 */
export function generateDailySummary(
  dashboard: DashboardData,
  crisisGauge?: CrisisGaugeData | null
): string {
  const silverPrice = dashboard.prices?.silver?.price || 0
  const silverChange = dashboard.prices?.silver?.change_pct || 0
  const phase = crisisGauge?.current_phase || 2
  const cracksShowing = crisisGauge?.cracks_showing_count || 0
  const crisisProbability = crisisGauge?.crisis_probability || 0

  const lines: string[] = []

  // Silver movement
  if (Math.abs(silverChange) >= 1) {
    lines.push(`Silver ${silverChange > 0 ? 'gained' : 'dropped'} ${Math.abs(silverChange).toFixed(1)}% to $${silverPrice.toFixed(2)}`)
  } else {
    lines.push(`Silver trading at $${silverPrice.toFixed(2)} with minimal movement`)
  }

  // Phase status
  const phaseNames = ['Stable', 'Elevated', 'Stressed', 'Critical', 'Systemic']
  lines.push(`Crisis cascade at Phase ${phase} (${phaseNames[phase - 1] || 'Unknown'})`)

  // Cracks status
  if (cracksShowing > 0) {
    lines.push(`${cracksShowing} stress indicator${cracksShowing > 1 ? 's' : ''} showing warning signs`)
  } else {
    lines.push('No early warning indicators active')
  }

  return lines.join('. ') + '.'
}

/**
 * Determine if any important thresholds were crossed
 */
export function checkThresholdCrossings(
  currentPrice: number,
  previousPrice: number,
  currentPhase: number,
  previousPhase: number
): string[] {
  const crossings: string[] = []

  // Silver price thresholds
  const priceThresholds = [50, 75, 100, 125, 150]
  for (const threshold of priceThresholds) {
    if (previousPrice < threshold && currentPrice >= threshold) {
      crossings.push(`Silver crossed $${threshold}`)
    }
    if (previousPrice >= threshold && currentPrice < threshold) {
      crossings.push(`Silver fell below $${threshold}`)
    }
  }

  // Phase changes
  if (currentPhase > previousPhase) {
    crossings.push(`Cascade advanced to Phase ${currentPhase}`)
  }
  if (currentPhase < previousPhase) {
    crossings.push(`Cascade de-escalated to Phase ${currentPhase}`)
  }

  return crossings
}

/**
 * Format date for display
 */
export function formatScanDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
