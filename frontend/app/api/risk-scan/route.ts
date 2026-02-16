import { NextResponse } from 'next/server'
import { generateDailyHeadline, generateDailySummary, formatScanDate } from '@/lib/risk-headline'
import { api } from '@/lib/api'

// In-memory cache for the latest scan
let cachedScan: {
  timestamp: Date
  headline: string
  summary: string
  direction: string
  severity: string
  silverPrice: number
  silverChange: number
  phase: number
  cracksShowing: number
} | null = null

/**
 * GET /api/risk-scan
 * Returns the latest risk scan data
 */
export async function GET() {
  try {
    // Return cached scan if fresh (within 4 hours)
    if (cachedScan) {
      const age = Date.now() - cachedScan.timestamp.getTime()
      const fourHours = 4 * 60 * 60 * 1000
      if (age < fourHours) {
        return NextResponse.json({
          ...cachedScan,
          cached: true,
          age: Math.round(age / 1000 / 60) // age in minutes
        })
      }
    }

    // Fetch fresh data
    const [dashboard, crisisGauge] = await Promise.all([
      api.getDashboard(),
      api.getCrisisGauge()
    ])

    // Generate headline and summary
    const headline = generateDailyHeadline(dashboard, crisisGauge)
    const summary = generateDailySummary(dashboard, crisisGauge)

    // Update cache
    cachedScan = {
      timestamp: new Date(),
      headline: headline.headline,
      summary,
      direction: headline.direction,
      severity: headline.severity,
      silverPrice: dashboard.prices?.silver?.price || 0,
      silverChange: dashboard.prices?.silver?.change_pct || 0,
      phase: crisisGauge?.current_phase || 2,
      cracksShowing: crisisGauge?.cracks_showing_count || 0
    }

    return NextResponse.json({
      ...cachedScan,
      cached: false,
      formattedDate: formatScanDate(cachedScan.timestamp)
    })
  } catch (error) {
    console.error('Risk scan error:', error)
    return NextResponse.json(
      { error: 'Failed to generate risk scan' },
      { status: 500 }
    )
  }
}

/**
 * POST /api/risk-scan
 * Forces a fresh scan (for cron jobs)
 */
export async function POST() {
  try {
    // Clear cache to force fresh scan
    cachedScan = null

    // Call GET to perform the scan
    const result = await GET()
    return result
  } catch (error) {
    console.error('Risk scan refresh error:', error)
    return NextResponse.json(
      { error: 'Failed to refresh risk scan' },
      { status: 500 }
    )
  }
}
