/**
 * Hourly Parameter Search Cron Worker
 *
 * This script runs as a separate Fly.io process and triggers the
 * hourly parameter search API endpoint every hour.
 *
 * The API endpoint handles EST window enforcement (05:00-22:00),
 * so this cron runs 24/7 UTC and the API decides whether to execute.
 */

const API_URL = process.env.HOURLY_SEARCH_API_URL || 'http://localhost:3000/api/hourly-parameter-search'
const API_KEY = process.env.HOURLY_SEARCH_API_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY

// Interval in milliseconds (1 hour = 3600000ms)
const INTERVAL_MS = 60 * 60 * 1000

// Calculate milliseconds until next hour
function msUntilNextHour(): number {
  const now = new Date()
  const nextHour = new Date(now)
  nextHour.setHours(now.getHours() + 1)
  nextHour.setMinutes(0)
  nextHour.setSeconds(0)
  nextHour.setMilliseconds(0)
  return nextHour.getTime() - now.getTime()
}

// Format date for logging
function formatTime(date: Date): string {
  return date.toISOString().replace('T', ' ').substring(0, 19)
}

// Call the hourly parameter search API
async function triggerHourlySearch(): Promise<void> {
  const startTime = new Date()
  console.log(`[${formatTime(startTime)}] Triggering hourly parameter search...`)

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (API_KEY) {
      headers['Authorization'] = `Bearer ${API_KEY}`
    }

    const response = await fetch(API_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify({ mode: 'hourly_parameter_search' }),
    })

    const result = await response.json()

    const endTime = new Date()
    const durationMs = endTime.getTime() - startTime.getTime()

    if (response.ok) {
      console.log(`[${formatTime(endTime)}] Search completed in ${durationMs}ms`)
      console.log(`  Status: ${result.status}`)
      console.log(`  Run ID: ${result.run_id}`)

      if (result.status === 'completed' && result.sheets) {
        const totalNew = result.sheets.reduce((sum: number, s: { new_items: number }) => sum + s.new_items, 0)
        const totalErrors = result.sheets.reduce((sum: number, s: { errors: number }) => sum + s.errors, 0)
        console.log(`  New items: ${totalNew}`)
        console.log(`  Errors: ${totalErrors}`)
      } else if (result.status === 'skipped_outside_window') {
        console.log('  Reason: Outside EST active window (05:00-22:00)')
      }
    } else {
      console.error(`[${formatTime(endTime)}] Search failed with status ${response.status}`)
      console.error(`  Error: ${result.error || 'Unknown error'}`)
    }
  } catch (error) {
    const endTime = new Date()
    console.error(`[${formatTime(endTime)}] Failed to trigger search:`, error)
  }
}

// Main cron loop
async function main(): Promise<void> {
  console.log('='.repeat(60))
  console.log('Fault.Watch Hourly Parameter Search Cron Worker')
  console.log('='.repeat(60))
  console.log(`API URL: ${API_URL}`)
  console.log(`API Key: ${API_KEY ? 'Set' : 'Not set'}`)
  console.log(`Started at: ${formatTime(new Date())}`)
  console.log('='.repeat(60))

  // Wait until the top of the next hour before starting the regular interval
  const waitMs = msUntilNextHour()
  console.log(`Waiting ${Math.round(waitMs / 1000)}s until next hour...`)

  // Run immediately on startup (for testing and initial catchup)
  await triggerHourlySearch()

  // Then wait until the top of the next hour
  await new Promise(resolve => setTimeout(resolve, waitMs))

  // Start the hourly interval
  console.log(`Starting hourly interval at ${formatTime(new Date())}`)

  // Run at the top of each hour
  setInterval(async () => {
    await triggerHourlySearch()
  }, INTERVAL_MS)

  // Also run immediately after the wait
  await triggerHourlySearch()
}

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down...')
  process.exit(0)
})

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down...')
  process.exit(0)
})

// Start the cron worker
main().catch(error => {
  console.error('Cron worker failed:', error)
  process.exit(1)
})
