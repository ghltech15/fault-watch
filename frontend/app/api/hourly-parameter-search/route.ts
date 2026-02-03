/**
 * Hourly Parameter Search API Route
 *
 * Runs every hour (triggered by Fly.io cron), iterates through Parameter Sheets 1-5,
 * executes configured searches, and persists results to Supabase.
 *
 * Active window: 05:00 - 22:00 EST (America/New_York)
 * Outside this window: logs a "skipped" run and exits
 */

import { NextRequest, NextResponse } from 'next/server'
import { v4 as uuidv4 } from 'uuid'
import {
  getSupabaseServer,
  Sheet1Parameter,
  Sheet2Parameter,
  Sheet3Parameter,
  Sheet4Parameter,
  Sheet5Parameter,
  SheetSummary,
  RunPayload,
  RunStatus,
} from '@/lib/supabase-server'

// Backend API base URL (Fly.io hosted FastAPI)
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

// ============================================
// Timezone Utilities
// ============================================

/**
 * Get current time in America/New_York (EST/EDT)
 */
function getNowEST(): Date {
  return new Date(
    new Date().toLocaleString('en-US', { timeZone: 'America/New_York' })
  )
}

/**
 * Check if current EST time is within active window (05:00 - 22:00)
 */
function isWithinActiveWindow(): boolean {
  const nowEST = getNowEST()
  const hour = nowEST.getHours()
  return hour >= 5 && hour < 22
}

/**
 * Get the current EST hour boundaries
 */
function getESTHourBoundaries(): { start: string; end: string } {
  const nowEST = getNowEST()
  const hourStart = new Date(nowEST)
  hourStart.setMinutes(0, 0, 0)

  const hourEnd = new Date(hourStart)
  hourEnd.setHours(hourStart.getHours() + 1)

  // Format with EST offset
  const formatWithOffset = (d: Date) => {
    const iso = d.toISOString().slice(0, 19)
    // Determine if we're in EST (-05:00) or EDT (-04:00)
    const jan = new Date(d.getFullYear(), 0, 1)
    const jul = new Date(d.getFullYear(), 6, 1)
    const stdOffset = Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset())
    const isDST = d.getTimezoneOffset() < stdOffset
    const offset = isDST ? '-04:00' : '-05:00'
    return `${iso}${offset}`
  }

  return {
    start: formatWithOffset(hourStart),
    end: formatWithOffset(hourEnd),
  }
}

// ============================================
// Backend API Callers
// ============================================

type SearchFunction = (
  param: Sheet1Parameter | Sheet2Parameter | Sheet3Parameter | Sheet4Parameter | Sheet5Parameter
) => Promise<SearchResult>

interface SearchResult {
  items: unknown[]
  newItems: number
  updatedItems: number
  hash: string
  error?: string
}

/**
 * Call backend API endpoint
 */
async function callBackendAPI(endpoint: string): Promise<unknown> {
  try {
    const response = await fetch(`${BACKEND_API_URL}${endpoint}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      // 30 second timeout
      signal: AbortSignal.timeout(30000),
    })

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`Backend API call failed for ${endpoint}:`, error)
    throw error
  }
}

/**
 * Simple hash function for result deduplication
 */
function hashResults(items: unknown[]): string {
  const str = JSON.stringify(items)
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16)
}

/**
 * Search Sheet 1: Regulators & Official Filings
 */
async function searchSheet1(param: Sheet1Parameter): Promise<SearchResult> {
  const items: unknown[] = []
  let error: string | undefined

  try {
    // Map sources to backend endpoints
    const sourceEndpoints: Record<string, string> = {
      sec: '/api/pipeline/sec',
      sec_critical: '/api/pipeline/sec/critical',
      regulatory: '/api/pipeline/regulatory',
      events: '/api/events',
    }

    for (const source of param.sources) {
      const endpoint = sourceEndpoints[source]
      if (endpoint) {
        try {
          const data = await callBackendAPI(endpoint)
          if (Array.isArray(data)) {
            items.push(...data.slice(0, param.max_results_per_run))
          } else if (typeof data === 'object' && data !== null) {
            // If it's an object with an items/data array, extract it
            const arr = (data as Record<string, unknown>).items ||
                       (data as Record<string, unknown>).data ||
                       (data as Record<string, unknown>).filings ||
                       [data]
            if (Array.isArray(arr)) {
              items.push(...arr.slice(0, param.max_results_per_run))
            }
          }
        } catch (e) {
          console.error(`Sheet 1 source ${source} failed:`, e)
        }
      }
    }

    // Filter by entities if specified
    if (param.entities && param.entities.length > 0) {
      // Filter logic would go here based on entity matching
    }

    // Filter by filing types if specified
    if (param.filing_types && param.filing_types.length > 0) {
      // Filter logic would go here based on filing type matching
    }
  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error'
  }

  const hash = hashResults(items)
  const isNew = param.last_result_hash !== hash

  return {
    items: items.slice(0, param.max_results_per_run),
    newItems: isNew ? items.length : 0,
    updatedItems: isNew ? 0 : items.length,
    hash,
    error,
  }
}

/**
 * Search Sheet 2: News & RSS
 */
async function searchSheet2(param: Sheet2Parameter): Promise<SearchResult> {
  const items: unknown[] = []
  let error: string | undefined

  try {
    // Call news pipeline endpoints
    const endpoints = ['/api/pipeline/news', '/api/pipeline/news/breaking']

    for (const endpoint of endpoints) {
      try {
        const data = await callBackendAPI(endpoint)
        if (Array.isArray(data)) {
          items.push(...data)
        } else if (typeof data === 'object' && data !== null) {
          const arr = (data as Record<string, unknown>).items ||
                     (data as Record<string, unknown>).articles ||
                     (data as Record<string, unknown>).news ||
                     []
          if (Array.isArray(arr)) {
            items.push(...arr)
          }
        }
      } catch (e) {
        console.error(`Sheet 2 endpoint ${endpoint} failed:`, e)
      }
    }

    // Filter by publisher whitelist/blacklist
    // (would need item structure to implement properly)

  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error'
  }

  const hash = hashResults(items)
  const isNew = param.last_result_hash !== hash

  return {
    items: items.slice(0, param.max_results_per_run),
    newItems: isNew ? items.length : 0,
    updatedItems: isNew ? 0 : items.length,
    hash,
    error,
  }
}

/**
 * Search Sheet 3: Social Media & Sentiment
 */
async function searchSheet3(param: Sheet3Parameter): Promise<SearchResult> {
  const items: unknown[] = []
  let error: string | undefined

  try {
    // Call social pipeline endpoint
    const data = await callBackendAPI('/api/pipeline/social')
    if (Array.isArray(data)) {
      items.push(...data)
    } else if (typeof data === 'object' && data !== null) {
      const arr = (data as Record<string, unknown>).items ||
                 (data as Record<string, unknown>).posts ||
                 (data as Record<string, unknown>).social ||
                 []
      if (Array.isArray(arr)) {
        items.push(...arr)
      }
    }

    // Also fetch claims (often from social sources)
    try {
      const claims = await callBackendAPI('/api/claims')
      if (Array.isArray(claims)) {
        items.push(...claims)
      } else if (typeof claims === 'object' && claims !== null) {
        const arr = (claims as Record<string, unknown>).items ||
                   (claims as Record<string, unknown>).claims ||
                   []
        if (Array.isArray(arr)) {
          items.push(...arr)
        }
      }
    } catch (e) {
      console.error('Claims fetch failed:', e)
    }

    // Filter by min engagement if specified
    if (param.min_karma_or_engagement > 0) {
      // Filter logic would go here
    }

  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error'
  }

  const hash = hashResults(items)
  const isNew = param.last_result_hash !== hash

  return {
    items: items.slice(0, param.max_results_per_run),
    newItems: isNew ? items.length : 0,
    updatedItems: isNew ? 0 : items.length,
    hash,
    error,
  }
}

/**
 * Search Sheet 4: Market Structure & Data Feeds
 */
async function searchSheet4(param: Sheet4Parameter): Promise<SearchResult> {
  const items: unknown[] = []
  let error: string | undefined

  try {
    // Map data vendors to endpoints
    const vendorEndpoints: Record<string, string[]> = {
      cme: ['/api/pipeline/dealers', '/api/watchlist/backwardation'],
      lbma: ['/api/watchlist/shanghai-premium'],
      fred: ['/api/scores/funding'],
      ishares: ['/api/watchlist/slv-nav'],
    }

    const instrumentEndpoints: Record<string, string[]> = {
      inventory: ['/api/scores/deliverability', '/api/pipeline/dealers'],
      futures: ['/api/watchlist/backwardation', '/api/watchlist/cot'],
      etf: ['/api/watchlist/slv-nav'],
      repo: ['/api/scores/funding'],
    }

    // Call vendor-specific endpoints
    if (param.data_vendor && vendorEndpoints[param.data_vendor]) {
      for (const endpoint of vendorEndpoints[param.data_vendor]) {
        try {
          const data = await callBackendAPI(endpoint)
          items.push(data)
        } catch (e) {
          console.error(`Vendor endpoint ${endpoint} failed:`, e)
        }
      }
    }

    // Call instrument-specific endpoints
    if (param.instrument_type && instrumentEndpoints[param.instrument_type]) {
      for (const endpoint of instrumentEndpoints[param.instrument_type]) {
        try {
          const data = await callBackendAPI(endpoint)
          items.push(data)
        } catch (e) {
          console.error(`Instrument endpoint ${endpoint} failed:`, e)
        }
      }
    }

    // Default: fetch general market signals
    if (items.length === 0) {
      try {
        const signals = await callBackendAPI('/api/watchlist/signals')
        items.push(signals)
      } catch (e) {
        console.error('Signals fetch failed:', e)
      }
    }

  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error'
  }

  const hash = hashResults(items)
  const isNew = param.last_result_hash !== hash

  return {
    items: items.slice(0, param.max_results_per_run),
    newItems: isNew ? items.length : 0,
    updatedItems: isNew ? 0 : items.length,
    hash,
    error,
  }
}

/**
 * Search Sheet 5: Price/Alert Triggers
 */
async function searchSheet5(param: Sheet5Parameter): Promise<SearchResult> {
  const items: unknown[] = []
  let error: string | undefined
  let triggered = false

  try {
    // Fetch current prices
    const prices = await callBackendAPI('/api/prices') as Record<string, unknown>

    // Check if this trigger's threshold is met
    if (param.asset && param.threshold_type && param.threshold_value !== null) {
      const assetPrice = prices[param.asset] as number | undefined

      if (assetPrice !== undefined) {
        switch (param.threshold_type) {
          case '>=':
            triggered = assetPrice >= param.threshold_value
            break
          case '<=':
            triggered = assetPrice <= param.threshold_value
            break
          case '>':
            triggered = assetPrice > param.threshold_value
            break
          case '<':
            triggered = assetPrice < param.threshold_value
            break
          case 'crosses_above':
            // Would need historical data to implement
            triggered = assetPrice >= param.threshold_value
            break
          case 'crosses_below':
            triggered = assetPrice <= param.threshold_value
            break
        }

        items.push({
          asset: param.asset,
          current_price: assetPrice,
          threshold: param.threshold_value,
          threshold_type: param.threshold_type,
          triggered,
          checked_at: new Date().toISOString(),
        })
      }
    }

    // Also check alerts pipeline
    try {
      const alerts = await callBackendAPI('/api/pipeline/alerts')
      if (Array.isArray(alerts)) {
        items.push(...alerts)
      }
    } catch (e) {
      console.error('Alerts fetch failed:', e)
    }

  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error'
  }

  const hash = hashResults(items)
  const isNew = param.last_result_hash !== hash || triggered

  return {
    items: items.slice(0, param.max_results_per_run),
    newItems: isNew ? items.length : 0,
    updatedItems: isNew ? 0 : items.length,
    hash,
    error,
  }
}

// ============================================
// Main Handler
// ============================================

export async function POST(request: NextRequest) {
  const runId = uuidv4()
  const runStartedAt = new Date().toISOString()
  const estBoundaries = getESTHourBoundaries()

  // Parse request body
  let body: { mode?: string } = {}
  try {
    body = await request.json()
  } catch {
    // Default to hourly_parameter_search mode
  }

  // Validate mode (future-proofing)
  if (body.mode && body.mode !== 'hourly_parameter_search') {
    return NextResponse.json(
      { error: `Unknown mode: ${body.mode}` },
      { status: 400 }
    )
  }

  // Check authorization (service key or internal call)
  const authHeader = request.headers.get('Authorization')
  const expectedKey = process.env.HOURLY_SEARCH_API_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY

  // Allow if:
  // 1. No key is configured (development)
  // 2. Authorization header matches
  // 3. Request is from localhost/internal
  const isAuthorized =
    !expectedKey ||
    authHeader === `Bearer ${expectedKey}` ||
    request.headers.get('host')?.includes('localhost')

  if (!isAuthorized) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  // Initialize Supabase client
  let supabase
  try {
    supabase = getSupabaseServer()
  } catch (e) {
    console.error('Failed to initialize Supabase:', e)
    return NextResponse.json(
      {
        run_id: runId,
        status: 'error' as RunStatus,
        error: 'Failed to initialize database connection',
      },
      { status: 500 }
    )
  }

  // Check if within active window (05:00 - 22:00 EST)
  if (!isWithinActiveWindow()) {
    const skipPayload: RunPayload = {
      run_id: runId,
      status: 'skipped_outside_window',
      run_started_at_utc: runStartedAt,
      run_completed_at_utc: new Date().toISOString(),
      est_hour_start: estBoundaries.start,
      est_hour_end: estBoundaries.end,
      sheets: [],
    }

    // Log skipped run
    await supabase.from('fault_watch_parameter_runs').insert({
      run_id: runId,
      status: 'skipped_outside_window',
      run_started_at_utc: runStartedAt,
      run_completed_at_utc: new Date().toISOString(),
      est_hour_start: estBoundaries.start,
      est_hour_end: estBoundaries.end,
      skip_reason: 'Outside EST active window (05:00-22:00)',
      sheets_summary: [],
    })

    return NextResponse.json(skipPayload)
  }

  // Create pending run record
  await supabase.from('fault_watch_parameter_runs').insert({
    run_id: runId,
    status: 'running',
    run_started_at_utc: runStartedAt,
    est_hour_start: estBoundaries.start,
    est_hour_end: estBoundaries.end,
    sheets_summary: [],
  })

  // Process all 5 sheets
  const sheetsSummary: SheetSummary[] = []
  let totalRowsProcessed = 0
  let totalNewItems = 0
  let totalUpdatedItems = 0
  let totalSkippedRows = 0
  let totalErrors = 0

  // Sheet 1: Regulators
  const sheet1Summary = await processSheet(
    supabase,
    runId,
    1,
    'fault_watch_parameters_sheet1',
    searchSheet1 as SearchFunction
  )
  sheetsSummary.push(sheet1Summary)
  totalRowsProcessed += sheet1Summary.rows_processed
  totalNewItems += sheet1Summary.new_items
  totalUpdatedItems += sheet1Summary.updated_items
  totalSkippedRows += sheet1Summary.skipped_rows
  totalErrors += sheet1Summary.errors

  // Sheet 2: News
  const sheet2Summary = await processSheet(
    supabase,
    runId,
    2,
    'fault_watch_parameters_sheet2',
    searchSheet2 as SearchFunction
  )
  sheetsSummary.push(sheet2Summary)
  totalRowsProcessed += sheet2Summary.rows_processed
  totalNewItems += sheet2Summary.new_items
  totalUpdatedItems += sheet2Summary.updated_items
  totalSkippedRows += sheet2Summary.skipped_rows
  totalErrors += sheet2Summary.errors

  // Sheet 3: Social
  const sheet3Summary = await processSheet(
    supabase,
    runId,
    3,
    'fault_watch_parameters_sheet3',
    searchSheet3 as SearchFunction
  )
  sheetsSummary.push(sheet3Summary)
  totalRowsProcessed += sheet3Summary.rows_processed
  totalNewItems += sheet3Summary.new_items
  totalUpdatedItems += sheet3Summary.updated_items
  totalSkippedRows += sheet3Summary.skipped_rows
  totalErrors += sheet3Summary.errors

  // Sheet 4: Market Structure
  const sheet4Summary = await processSheet(
    supabase,
    runId,
    4,
    'fault_watch_parameters_sheet4',
    searchSheet4 as SearchFunction
  )
  sheetsSummary.push(sheet4Summary)
  totalRowsProcessed += sheet4Summary.rows_processed
  totalNewItems += sheet4Summary.new_items
  totalUpdatedItems += sheet4Summary.updated_items
  totalSkippedRows += sheet4Summary.skipped_rows
  totalErrors += sheet4Summary.errors

  // Sheet 5: Price Triggers
  const sheet5Summary = await processSheet(
    supabase,
    runId,
    5,
    'fault_watch_parameters_sheet5',
    searchSheet5 as SearchFunction
  )
  sheetsSummary.push(sheet5Summary)
  totalRowsProcessed += sheet5Summary.rows_processed
  totalNewItems += sheet5Summary.new_items
  totalUpdatedItems += sheet5Summary.updated_items
  totalSkippedRows += sheet5Summary.skipped_rows
  totalErrors += sheet5Summary.errors

  // Update run record with completion
  const runCompletedAt = new Date().toISOString()
  await supabase
    .from('fault_watch_parameter_runs')
    .update({
      status: 'completed',
      run_completed_at_utc: runCompletedAt,
      total_rows_processed: totalRowsProcessed,
      total_new_items: totalNewItems,
      total_updated_items: totalUpdatedItems,
      total_skipped_rows: totalSkippedRows,
      total_errors: totalErrors,
      sheets_summary: sheetsSummary,
    })
    .eq('run_id', runId)

  // Return run payload
  const payload: RunPayload = {
    run_id: runId,
    status: 'completed',
    run_started_at_utc: runStartedAt,
    run_completed_at_utc: runCompletedAt,
    est_hour_start: estBoundaries.start,
    est_hour_end: estBoundaries.end,
    sheets: sheetsSummary,
  }

  return NextResponse.json(payload)
}

/**
 * Process a single parameter sheet
 */
async function processSheet(
  supabase: ReturnType<typeof getSupabaseServer>,
  runId: string,
  sheetNumber: number,
  tableName: string,
  searchFn: SearchFunction
): Promise<SheetSummary> {
  const summary: SheetSummary = {
    sheet_number: sheetNumber,
    rows_processed: 0,
    new_items: 0,
    updated_items: 0,
    skipped_rows: 0,
    errors: 0,
    notes: null,
  }

  const notes: string[] = []

  try {
    // Fetch enabled parameters for this sheet
    const { data: params, error: fetchError } = await supabase
      .from(tableName)
      .select('*')
      .eq('is_enabled', true)
      .order('priority', { ascending: true })

    if (fetchError) {
      summary.errors = 1
      summary.notes = `Failed to fetch parameters: ${fetchError.message}`
      return summary
    }

    if (!params || params.length === 0) {
      summary.notes = 'No enabled parameters found'
      return summary
    }

    // Process each parameter row
    for (const param of params) {
      try {
        // Check cooldown
        if (param.cooldown_minutes && param.last_run_at) {
          const lastRun = new Date(param.last_run_at)
          const cooldownMs = param.cooldown_minutes * 60 * 1000
          if (Date.now() - lastRun.getTime() < cooldownMs) {
            summary.skipped_rows++
            notes.push(`${param.name}: skipped (cooldown)`)
            continue
          }
        }

        // Check max runs per day
        if (param.max_runs_per_day) {
          const today = new Date().toISOString().split('T')[0]
          const { count } = await supabase
            .from('fault_watch_parameter_results')
            .select('*', { count: 'exact', head: true })
            .eq('parameter_id', param.id)
            .gte('executed_at', `${today}T00:00:00Z`)

          if (count !== null && count >= param.max_runs_per_day) {
            summary.skipped_rows++
            notes.push(`${param.name}: skipped (max runs/day)`)
            continue
          }
        }

        // Execute search
        const result = await searchFn(param)
        summary.rows_processed++

        if (result.error) {
          summary.errors++
          notes.push(`${param.name}: error - ${result.error}`)

          // Log error result
          await supabase.from('fault_watch_parameter_results').insert({
            run_id: runId,
            sheet_number: sheetNumber,
            parameter_id: param.id,
            parameter_name: param.name,
            items_found: 0,
            new_items: 0,
            updated_items: 0,
            error_message: result.error,
          })
        } else {
          summary.new_items += result.newItems
          summary.updated_items += result.updatedItems

          // Log successful result
          await supabase.from('fault_watch_parameter_results').insert({
            run_id: runId,
            sheet_number: sheetNumber,
            parameter_id: param.id,
            parameter_name: param.name,
            items_found: result.items.length,
            new_items: result.newItems,
            updated_items: result.updatedItems,
            result_hash: result.hash,
            sample_results: result.items.slice(0, 5), // Store first 5 as sample
          })

          // Update parameter's last_run_at and last_result_hash
          await supabase
            .from(tableName)
            .update({
              last_run_at: new Date().toISOString(),
              last_result_hash: result.hash,
            })
            .eq('id', param.id)
        }
      } catch (e) {
        summary.errors++
        const errorMsg = e instanceof Error ? e.message : 'Unknown error'
        notes.push(`${param.name}: exception - ${errorMsg}`)
        console.error(`Error processing parameter ${param.name}:`, e)
      }
    }
  } catch (e) {
    summary.errors++
    summary.notes = `Sheet processing failed: ${e instanceof Error ? e.message : 'Unknown error'}`
    return summary
  }

  summary.notes = notes.length > 0 ? notes.join('; ') : null
  return summary
}

// Also support GET for health checks
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'hourly-parameter-search',
    timestamp: new Date().toISOString(),
    est_time: getNowEST().toISOString(),
    within_active_window: isWithinActiveWindow(),
    active_window: '05:00-22:00 EST',
  })
}
