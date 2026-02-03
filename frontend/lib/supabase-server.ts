/**
 * Server-side Supabase client for API routes
 * Uses service role key for full database access
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://xieyimjykzccrjmlqdps.supabase.co'
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

// Create a server-side client with service role key
export function getSupabaseServer(): SupabaseClient {
  if (!supabaseServiceKey) {
    throw new Error('SUPABASE_SERVICE_ROLE_KEY is not set')
  }

  return createClient(supabaseUrl, supabaseServiceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  })
}

// ============================================
// Type definitions for parameter search system
// ============================================

export type SearchType = 'regulatory_filings' | 'news' | 'social' | 'market_data' | 'price_trigger'
export type SeverityLevel = 'info' | 'watch' | 'warning' | 'critical'
export type RunStatus = 'pending' | 'running' | 'completed' | 'skipped_outside_window' | 'error'

// Common fields for all parameter sheets
export interface BaseParameter {
  id: string
  sheet_number: number
  name: string
  description: string | null
  is_enabled: boolean
  priority: number
  search_query: string
  keywords: string[]
  sources: string[]
  search_type: SearchType
  max_results_per_run: number
  max_runs_per_day: number | null
  cooldown_minutes: number | null
  last_run_at: string | null
  last_result_hash: string | null
  severity_level: SeverityLevel
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

// Sheet 1: Regulators & Official Filings
export interface Sheet1Parameter extends BaseParameter {
  filing_types: string[]
  entities: string[]
}

// Sheet 2: News & RSS
export interface Sheet2Parameter extends BaseParameter {
  rss_feeds: string[]
  publisher_whitelist: string[]
  publisher_blacklist: string[]
}

// Sheet 3: Social Media & Sentiment
export interface Sheet3Parameter extends BaseParameter {
  platforms: string[]
  subreddits_or_handles: string[]
  min_karma_or_engagement: number
}

// Sheet 4: Market Structure & Data Feeds
export interface Sheet4Parameter extends BaseParameter {
  instrument_type: string | null
  symbols: string[]
  data_vendor: string | null
}

// Sheet 5: Price/Alert Triggers
export interface Sheet5Parameter extends BaseParameter {
  asset: string | null
  threshold_type: string | null
  threshold_value: number | null
  secondary_condition: Record<string, unknown> | null
  alert_channel: string
}

// Parameter run record
export interface ParameterRun {
  id: string
  run_id: string
  status: RunStatus
  run_started_at_utc: string
  run_completed_at_utc: string | null
  est_hour_start: string
  est_hour_end: string
  total_rows_processed: number
  total_new_items: number
  total_updated_items: number
  total_skipped_rows: number
  total_errors: number
  skip_reason: string | null
  error_message: string | null
  sheets_summary: SheetSummary[]
  created_at: string
}

// Sheet summary in run result
export interface SheetSummary {
  sheet_number: number
  rows_processed: number
  new_items: number
  updated_items: number
  skipped_rows: number
  errors: number
  notes: string | null
}

// Parameter result record
export interface ParameterResult {
  id: string
  run_id: string
  sheet_number: number
  parameter_id: string
  parameter_name: string | null
  items_found: number
  new_items: number
  updated_items: number
  result_hash: string | null
  event_store_ids: string[]
  sample_results: unknown[]
  error_message: string | null
  executed_at: string
  created_at: string
}

// Run payload (API response)
export interface RunPayload {
  run_id: string
  status: RunStatus
  run_started_at_utc: string
  run_completed_at_utc: string | null
  est_hour_start: string
  est_hour_end: string
  sheets: SheetSummary[]
}
