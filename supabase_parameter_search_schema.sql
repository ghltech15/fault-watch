-- ============================================
-- fault.watch - Hourly Parameter Search Schema
-- ============================================
-- Run this in your Supabase SQL Editor after supabase_schema.sql
-- Project URL: https://app.supabase.com/project/xieyimjykzccrjmlqdps/sql

-- ============================================
-- ENUM TYPES
-- ============================================

-- Search type enum
DO $$ BEGIN
    CREATE TYPE search_type AS ENUM (
        'regulatory_filings',
        'news',
        'social',
        'market_data',
        'price_trigger'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Severity level enum
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM (
        'info',
        'watch',
        'warning',
        'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Run status enum
DO $$ BEGIN
    CREATE TYPE run_status AS ENUM (
        'pending',
        'running',
        'completed',
        'skipped_outside_window',
        'error'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- TABLE: fault_watch_parameters_sheet1
-- Regulators & Official Filings (SEC, FDIC, OCC, Fed, BIS, IMF)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameters_sheet1 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number INTEGER NOT NULL DEFAULT 1 CHECK (sheet_number = 1),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    search_query TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    search_type search_type NOT NULL DEFAULT 'regulatory_filings',
    max_results_per_run INTEGER NOT NULL DEFAULT 20,
    max_runs_per_day INTEGER,
    cooldown_minutes INTEGER,
    last_run_at TIMESTAMPTZ,
    last_result_hash TEXT,
    severity_level severity_level NOT NULL DEFAULT 'info',
    metadata JSONB DEFAULT '{}',
    -- Sheet 1 specific: Regulators
    filing_types TEXT[] DEFAULT '{}',
    entities TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for enabled rows lookup
CREATE INDEX IF NOT EXISTS idx_sheet1_enabled ON fault_watch_parameters_sheet1 (is_enabled, priority DESC);

-- ============================================
-- TABLE: fault_watch_parameters_sheet2
-- News, Research, and RSS
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameters_sheet2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number INTEGER NOT NULL DEFAULT 2 CHECK (sheet_number = 2),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    search_query TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    search_type search_type NOT NULL DEFAULT 'news',
    max_results_per_run INTEGER NOT NULL DEFAULT 20,
    max_runs_per_day INTEGER,
    cooldown_minutes INTEGER,
    last_run_at TIMESTAMPTZ,
    last_result_hash TEXT,
    severity_level severity_level NOT NULL DEFAULT 'info',
    metadata JSONB DEFAULT '{}',
    -- Sheet 2 specific: News/RSS
    rss_feeds TEXT[] DEFAULT '{}',
    publisher_whitelist TEXT[] DEFAULT '{}',
    publisher_blacklist TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sheet2_enabled ON fault_watch_parameters_sheet2 (is_enabled, priority DESC);

-- ============================================
-- TABLE: fault_watch_parameters_sheet3
-- Social Media & Sentiment
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameters_sheet3 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number INTEGER NOT NULL DEFAULT 3 CHECK (sheet_number = 3),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    search_query TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    search_type search_type NOT NULL DEFAULT 'social',
    max_results_per_run INTEGER NOT NULL DEFAULT 20,
    max_runs_per_day INTEGER,
    cooldown_minutes INTEGER,
    last_run_at TIMESTAMPTZ,
    last_result_hash TEXT,
    severity_level severity_level NOT NULL DEFAULT 'info',
    metadata JSONB DEFAULT '{}',
    -- Sheet 3 specific: Social
    platforms TEXT[] DEFAULT '{}',
    subreddits_or_handles TEXT[] DEFAULT '{}',
    min_karma_or_engagement INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sheet3_enabled ON fault_watch_parameters_sheet3 (is_enabled, priority DESC);

-- ============================================
-- TABLE: fault_watch_parameters_sheet4
-- Market Structure & Data Feeds
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameters_sheet4 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number INTEGER NOT NULL DEFAULT 4 CHECK (sheet_number = 4),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    search_query TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    search_type search_type NOT NULL DEFAULT 'market_data',
    max_results_per_run INTEGER NOT NULL DEFAULT 20,
    max_runs_per_day INTEGER,
    cooldown_minutes INTEGER,
    last_run_at TIMESTAMPTZ,
    last_result_hash TEXT,
    severity_level severity_level NOT NULL DEFAULT 'info',
    metadata JSONB DEFAULT '{}',
    -- Sheet 4 specific: Market Structure
    instrument_type VARCHAR(50),
    symbols TEXT[] DEFAULT '{}',
    data_vendor VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sheet4_enabled ON fault_watch_parameters_sheet4 (is_enabled, priority DESC);

-- ============================================
-- TABLE: fault_watch_parameters_sheet5
-- Price/Alert Triggers & Special Watches
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameters_sheet5 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_number INTEGER NOT NULL DEFAULT 5 CHECK (sheet_number = 5),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    search_query TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    search_type search_type NOT NULL DEFAULT 'price_trigger',
    max_results_per_run INTEGER NOT NULL DEFAULT 20,
    max_runs_per_day INTEGER,
    cooldown_minutes INTEGER,
    last_run_at TIMESTAMPTZ,
    last_result_hash TEXT,
    severity_level severity_level NOT NULL DEFAULT 'info',
    metadata JSONB DEFAULT '{}',
    -- Sheet 5 specific: Price/Alert Triggers
    asset VARCHAR(50),
    threshold_type VARCHAR(20),
    threshold_value NUMERIC,
    secondary_condition JSONB,
    alert_channel VARCHAR(50) DEFAULT 'dashboard',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sheet5_enabled ON fault_watch_parameters_sheet5 (is_enabled, priority DESC);

-- ============================================
-- TABLE: fault_watch_parameter_runs
-- Tracks each hourly run execution
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameter_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL UNIQUE,
    status run_status NOT NULL DEFAULT 'pending',
    run_started_at_utc TIMESTAMPTZ NOT NULL,
    run_completed_at_utc TIMESTAMPTZ,
    est_hour_start TIMESTAMPTZ NOT NULL,
    est_hour_end TIMESTAMPTZ NOT NULL,
    total_rows_processed INTEGER DEFAULT 0,
    total_new_items INTEGER DEFAULT 0,
    total_updated_items INTEGER DEFAULT 0,
    total_skipped_rows INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    skip_reason TEXT,
    error_message TEXT,
    sheets_summary JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for recent runs lookup
CREATE INDEX IF NOT EXISTS idx_runs_started ON fault_watch_parameter_runs (run_started_at_utc DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON fault_watch_parameter_runs (status);

-- ============================================
-- TABLE: fault_watch_parameter_results
-- Summarized results per parameter row per run
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_parameter_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES fault_watch_parameter_runs(run_id) ON DELETE CASCADE,
    sheet_number INTEGER NOT NULL CHECK (sheet_number BETWEEN 1 AND 5),
    parameter_id UUID NOT NULL,
    parameter_name VARCHAR(100),
    items_found INTEGER DEFAULT 0,
    new_items INTEGER DEFAULT 0,
    updated_items INTEGER DEFAULT 0,
    result_hash TEXT,
    event_store_ids TEXT[] DEFAULT '{}',
    sample_results JSONB DEFAULT '[]',
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for run lookup
CREATE INDEX IF NOT EXISTS idx_results_run ON fault_watch_parameter_results (run_id);
CREATE INDEX IF NOT EXISTS idx_results_sheet ON fault_watch_parameter_results (sheet_number, parameter_id);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Enable RLS on all parameter tables
ALTER TABLE fault_watch_parameters_sheet1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameters_sheet2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameters_sheet3 ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameters_sheet4 ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameters_sheet5 ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameter_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_parameter_results ENABLE ROW LEVEL SECURITY;

-- Public read access for parameter sheets (config is public)
CREATE POLICY "Public read access" ON fault_watch_parameters_sheet1 FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_parameters_sheet2 FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_parameters_sheet3 FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_parameters_sheet4 FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_parameters_sheet5 FOR SELECT TO anon, authenticated USING (true);

-- Public read access for runs and results (monitoring is public)
CREATE POLICY "Public read access" ON fault_watch_parameter_runs FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_parameter_results FOR SELECT TO anon, authenticated USING (true);

-- Service role can do everything (for the API)
CREATE POLICY "Service role full access" ON fault_watch_parameters_sheet1 FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameters_sheet2 FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameters_sheet3 FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameters_sheet4 FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameters_sheet5 FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameter_runs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_parameter_results FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================
-- TRIGGERS: Auto-update updated_at
-- ============================================

CREATE TRIGGER update_sheet1_timestamp
    BEFORE UPDATE ON fault_watch_parameters_sheet1
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sheet2_timestamp
    BEFORE UPDATE ON fault_watch_parameters_sheet2
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sheet3_timestamp
    BEFORE UPDATE ON fault_watch_parameters_sheet3
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sheet4_timestamp
    BEFORE UPDATE ON fault_watch_parameters_sheet4
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sheet5_timestamp
    BEFORE UPDATE ON fault_watch_parameters_sheet5
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- SEED DATA: Example parameter rows
-- ============================================

-- Sheet 1: Regulators & Official Filings
INSERT INTO fault_watch_parameters_sheet1 (name, description, search_query, keywords, sources, filing_types, entities, priority, severity_level) VALUES
    ('MS SEC Filings', 'Monitor Morgan Stanley SEC filings for derivatives exposure', 'Morgan Stanley precious metals derivatives', ARRAY['morgan stanley', 'derivatives', 'precious metals', 'silver'], ARRAY['sec'], ARRAY['10-K', '10-Q', '8-K'], ARRAY['MS'], 1, 'critical'),
    ('Bank Enforcement Actions', 'Track SEC/CFTC enforcement actions against major banks', 'bank enforcement action precious metals manipulation', ARRAY['enforcement', 'manipulation', 'spoofing', 'fine'], ARRAY['sec', 'cftc'], ARRAY['Enforcement'], ARRAY['MS', 'JPM', 'C', 'GS', 'HSBC', 'UBS'], 1, 'critical'),
    ('FDIC Bank Failures', 'Monitor FDIC for bank failure announcements', 'bank failure FDIC closure', ARRAY['bank failure', 'fdic', 'closure', 'receivership'], ARRAY['fdic'], ARRAY['Press Release'], ARRAY[], 2, 'warning'),
    ('OCC Derivatives Report', 'Track OCC quarterly derivatives reports', 'OCC derivatives report precious metals', ARRAY['occ', 'derivatives', 'notional'], ARRAY['occ'], ARRAY['Quarterly Report'], ARRAY['JPM', 'C', 'BAC', 'GS'], 2, 'watch')
ON CONFLICT DO NOTHING;

-- Sheet 2: News & RSS
INSERT INTO fault_watch_parameters_sheet2 (name, description, search_query, keywords, sources, rss_feeds, publisher_whitelist, priority, severity_level) VALUES
    ('Silver Market News', 'Track silver market news from major outlets', 'silver price market squeeze shortage', ARRAY['silver', 'squeeze', 'shortage', 'delivery'], ARRAY['reuters', 'bloomberg', 'wsj'], ARRAY['https://www.kitco.com/news/rss/kitco-news-headlines.rss'], ARRAY['Reuters', 'Bloomberg', 'WSJ', 'FT', 'Kitco'], 2, 'watch'),
    ('Bank Crisis News', 'Monitor news about bank stress and failures', 'bank crisis liquidity stress failure', ARRAY['bank', 'crisis', 'liquidity', 'stress', 'failure'], ARRAY['reuters', 'bloomberg', 'ft'], ARRAY[], ARRAY['Reuters', 'Bloomberg', 'FT', 'WSJ'], 1, 'warning'),
    ('Fed Policy News', 'Track Federal Reserve policy announcements', 'federal reserve interest rate QE QT repo', ARRAY['fed', 'fomc', 'rate', 'repo', 'liquidity'], ARRAY['reuters', 'bloomberg'], ARRAY[], ARRAY['Reuters', 'Bloomberg', 'CNBC'], 2, 'info')
ON CONFLICT DO NOTHING;

-- Sheet 3: Social Media & Sentiment
INSERT INTO fault_watch_parameters_sheet3 (name, description, search_query, keywords, sources, platforms, subreddits_or_handles, min_karma_or_engagement, priority, severity_level) VALUES
    ('WallStreetSilver Sentiment', 'Monitor r/WallStreetSilver for squeeze sentiment', 'silver squeeze physical delivery COMEX drain', ARRAY['squeeze', 'physical', 'delivery', 'drain', 'apes'], ARRAY['reddit'], ARRAY['reddit'], ARRAY['wallstreetsilver'], 100, 2, 'info'),
    ('Bank Stock Sentiment', 'Track social sentiment on major bank stocks', 'Morgan Stanley Citi JPMorgan bank stock', ARRAY['MS', 'C', 'JPM', 'bank', 'short'], ARRAY['reddit', 'twitter'], ARRAY['reddit', 'twitter'], ARRAY['wallstreetbets', 'stocks'], 500, 3, 'info'),
    ('Silver Twitter', 'Monitor silver-focused Twitter accounts', 'silver price COMEX LBMA delivery', ARRAY['silver', 'comex', 'lbma'], ARRAY['twitter'], ARRAY['twitter'], ARRAY['SilverSqueeze', 'WallStreetSilv', 'TFMetals'], 50, 3, 'info')
ON CONFLICT DO NOTHING;

-- Sheet 4: Market Structure & Data Feeds
INSERT INTO fault_watch_parameters_sheet4 (name, description, search_query, keywords, sources, instrument_type, symbols, data_vendor, priority, severity_level) VALUES
    ('COMEX Silver Inventory', 'Track COMEX registered/eligible silver inventory', 'COMEX silver registered eligible inventory', ARRAY['comex', 'registered', 'eligible', 'inventory'], ARRAY['cme'], 'inventory', ARRAY['SI'], 'cme', 1, 'critical'),
    ('Silver Futures Open Interest', 'Monitor silver futures open interest for squeeze signals', 'silver futures open interest delivery', ARRAY['open interest', 'futures', 'delivery'], ARRAY['cme'], 'futures', ARRAY['SI'], 'cme', 1, 'warning'),
    ('SLV ETF Flows', 'Track SLV ETF inflows/outflows', 'SLV ETF flows holdings silver', ARRAY['slv', 'etf', 'flows', 'holdings'], ARRAY['ishares'], 'etf', ARRAY['SLV'], 'ishares', 2, 'watch'),
    ('Fed Repo Operations', 'Monitor Federal Reserve repo/reverse repo operations', 'fed repo reverse repo RRP SRF', ARRAY['repo', 'rrp', 'srf', 'liquidity'], ARRAY['fred', 'ny_fed'], 'repo', ARRAY[], 'fred', 1, 'warning'),
    ('LBMA Silver Holdings', 'Track LBMA vault silver holdings', 'LBMA silver vault holdings London', ARRAY['lbma', 'vault', 'london'], ARRAY['lbma'], 'inventory', ARRAY['XAG'], 'lbma', 2, 'watch')
ON CONFLICT DO NOTHING;

-- Sheet 5: Price/Alert Triggers
INSERT INTO fault_watch_parameters_sheet5 (name, description, search_query, keywords, sources, asset, threshold_type, threshold_value, secondary_condition, alert_channel, priority, severity_level) VALUES
    ('Silver $50 Breakout', 'Alert when silver breaks above $50', 'silver price breakout', ARRAY['silver', 'breakout'], ARRAY['prices'], 'XAGUSD', '>=', 50.00, NULL, 'dashboard', 1, 'critical'),
    ('Silver $100 Crisis', 'Critical alert for silver at $100', 'silver price crisis', ARRAY['silver', 'crisis'], ARRAY['prices'], 'XAGUSD', '>=', 100.00, NULL, 'dashboard', 1, 'critical'),
    ('MS -10% Daily Drop', 'Alert when MS drops 10% in a day', 'Morgan Stanley crash', ARRAY['MS', 'crash', 'drop'], ARRAY['prices'], 'MS', '<=', -10.00, '{"metric": "daily_change_pct"}', 'dashboard', 1, 'critical'),
    ('VIX Spike >40', 'Alert when VIX spikes above 40', 'VIX spike fear', ARRAY['vix', 'fear', 'volatility'], ARRAY['prices'], 'VIX', '>=', 40.00, NULL, 'dashboard', 1, 'warning'),
    ('Gold/Silver Ratio <50', 'Alert when gold/silver ratio drops below 50', 'gold silver ratio', ARRAY['ratio', 'silver', 'gold'], ARRAY['prices'], 'XAU_XAG_RATIO', '<=', 50.00, NULL, 'dashboard', 2, 'watch')
ON CONFLICT DO NOTHING;

-- ============================================
-- VIEWS
-- ============================================

-- View: Latest run status
CREATE OR REPLACE VIEW fault_watch_latest_run AS
SELECT
    run_id,
    status,
    run_started_at_utc,
    run_completed_at_utc,
    est_hour_start,
    total_rows_processed,
    total_new_items,
    total_errors,
    sheets_summary
FROM fault_watch_parameter_runs
ORDER BY run_started_at_utc DESC
LIMIT 1;

-- View: Run statistics (last 24 hours)
CREATE OR REPLACE VIEW fault_watch_run_stats_24h AS
SELECT
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_runs,
    COUNT(*) FILTER (WHERE status = 'skipped_outside_window') as skipped_runs,
    COUNT(*) FILTER (WHERE status = 'error') as error_runs,
    SUM(total_new_items) as total_new_items,
    SUM(total_errors) as total_errors,
    AVG(EXTRACT(EPOCH FROM (run_completed_at_utc - run_started_at_utc))) as avg_duration_seconds
FROM fault_watch_parameter_runs
WHERE run_started_at_utc >= NOW() - INTERVAL '24 hours';

-- ============================================
-- DONE!
-- ============================================
-- Run this SQL in Supabase SQL Editor to set up parameter search tables.
-- Then populate the parameter sheets with your specific search configurations.
