-- ============================================
-- fault.watch - Core Narrative Blocks Schema
-- ============================================
-- Run this AFTER supabase_parameter_search_schema.sql
-- These tables store the hourly "core narrative" blocks
-- that must run every hour from 5am-10pm EST

-- ============================================
-- TABLE: fault_watch_fdic_status
-- FDIC Failed Banks Status Block (8.1)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_fdic_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- Status
    has_new_failures BOOLEAN NOT NULL DEFAULT false,
    new_failures_count INTEGER DEFAULT 0,

    -- 2026 running count
    year_to_date_failures INTEGER NOT NULL DEFAULT 1,
    latest_failure_name TEXT DEFAULT 'Metropolitan Capital Bank & Trust',
    latest_failure_date DATE DEFAULT '2026-01-23',
    latest_failure_state TEXT DEFAULT 'IL',
    latest_failure_acquirer TEXT,
    latest_failure_reason TEXT,

    -- New failures details (if any)
    new_failures JSONB DEFAULT '[]',

    -- Unrealized losses context
    unrealized_losses_billions DECIMAL(10,2) DEFAULT 337.1,
    unrealized_losses_quarter TEXT DEFAULT 'Q3 2025',

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Sources
    sources JSONB DEFAULT '[]',

    -- Timestamps (required per section 9)
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,
    source_window_start_utc TIMESTAMPTZ,
    source_window_end_utc TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fdic_status_run ON fault_watch_fdic_status (run_id);
CREATE INDEX IF NOT EXISTS idx_fdic_status_generated ON fault_watch_fdic_status (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_ms_insider_tracker
-- Morgan Stanley Insider Selling Tracker (8.2)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_ms_insider_tracker (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- 90-day totals
    total_shares_sold_90d BIGINT DEFAULT 0,
    total_value_sold_90d DECIMAL(15,2) DEFAULT 0,
    total_shares_bought_90d BIGINT DEFAULT 0,
    total_value_bought_90d DECIMAL(15,2) DEFAULT 0,
    net_insider_flow TEXT DEFAULT 'selling-only',

    -- Recent trades (most recent first)
    recent_trades JSONB DEFAULT '[]',
    -- Example: [{"name": "Daniel Simkowitz", "shares": 32968, "price_range": "$182-183", "date": "2026-01-30", "pct_reduction": 15.2}]

    -- Insider pressure summary
    pressure_level TEXT DEFAULT 'high', -- low, moderate, high, extreme
    pressure_summary TEXT,

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Form 4 filings tracked
    form4_filings JSONB DEFAULT '[]',

    -- Timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,
    lookback_start_utc TIMESTAMPTZ,
    lookback_end_utc TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ms_insider_run ON fault_watch_ms_insider_tracker (run_id);
CREATE INDEX IF NOT EXISTS idx_ms_insider_generated ON fault_watch_ms_insider_tracker (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_flagstar_cre
-- Flagstar Risk/CRE Block (8.3)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_flagstar_cre (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- Q4 status
    q4_eps DECIMAL(6,2) DEFAULT 0.05,
    q4_eps_diluted BOOLEAN DEFAULT true,
    profitable_quarter BOOLEAN DEFAULT true,

    -- Forward guidance
    eps_guidance_2026_low DECIMAL(6,2),
    eps_guidance_2026_high DECIMAL(6,2),
    eps_guidance_2027_low DECIMAL(6,2),
    eps_guidance_2027_high DECIMAL(6,2),

    -- CRE metrics
    multifamily_cre_reduction_billions DECIMAL(6,2) DEFAULT 2.3,
    cre_concentration_ratio_pct DECIMAL(6,1) DEFAULT 381.0,
    cre_danger_zone_pct DECIMAL(6,1) DEFAULT 300.0,

    -- Upcoming events
    upcoming_events JSONB DEFAULT '[]',
    -- Example: [{"event": "Bank of America Securities conference", "location": "Miami", "date": "2026-02-10"}]

    -- Change detection
    has_material_updates BOOLEAN DEFAULT false,
    last_material_change_at TIMESTAMPTZ,
    no_change_note TEXT,

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Sources
    sources JSONB DEFAULT '[]',

    -- Timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flagstar_run ON fault_watch_flagstar_cre (run_id);
CREATE INDEX IF NOT EXISTS idx_flagstar_generated ON fault_watch_flagstar_cre (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_silver_status
-- Silver Price Block (8.4)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_silver_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- Current price
    current_price DECIMAL(10,2) NOT NULL,
    price_as_of_utc TIMESTAMPTZ NOT NULL,

    -- Intraday range
    intraday_low DECIMAL(10,2),
    intraday_high DECIMAL(10,2),

    -- Comparisons
    prior_close DECIMAL(10,2),
    change_from_close_pct DECIMAL(6,2),
    last_week_peak DECIMAL(10,2),
    change_from_peak_pct DECIMAL(6,2),

    -- Danger thresholds
    danger_threshold_95 DECIMAL(10,2) DEFAULT 95.00,
    distance_to_danger_pct DECIMAL(6,2),

    -- Movement context
    movement_direction TEXT, -- 'bouncing', 'falling', 'consolidating', 'surging'
    movement_explanation TEXT,
    key_catalysts JSONB DEFAULT '[]',

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_run ON fault_watch_silver_status (run_id);
CREATE INDEX IF NOT EXISTS idx_silver_generated ON fault_watch_silver_status (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_bank_selloff
-- Major Bank Sell-off Block (8.4)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_bank_selloff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- Sell-off status
    is_major_selloff BOOLEAN DEFAULT false,
    selloff_severity TEXT, -- 'minor', 'moderate', 'major', 'severe'

    -- Individual bank moves
    bank_moves JSONB DEFAULT '[]',
    -- Example: [{"ticker": "C", "name": "Citigroup", "change_pct": -3.4}, {"ticker": "BAC", "name": "Bank of America", "change_pct": -3.7}]

    -- Aggregate impact
    total_market_cap_lost_billions DECIMAL(10,2),

    -- Catalysts
    catalysts JSONB DEFAULT '[]',
    -- Example: ["Q4 earnings misses", "NII disappointments", "WFC asset cap removal uncertainty"]

    -- Banker Fear Index tie-in
    banker_fear_index_reading TEXT,
    systemic_risk_assessment TEXT,

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bank_selloff_run ON fault_watch_bank_selloff (run_id);
CREATE INDEX IF NOT EXISTS idx_bank_selloff_generated ON fault_watch_bank_selloff (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_banker_fear_index
-- Banker Fear Index Block (8.4)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_banker_fear_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES fault_watch_parameter_runs(run_id) ON DELETE SET NULL,

    -- Survey data
    tariff_volatility_threat_pct DECIMAL(5,2),
    recession_likelihood_us_pct DECIMAL(5,2),
    recession_likelihood_global_pct DECIMAL(5,2),
    govt_data_deterioration_risk_pct DECIMAL(5,2) DEFAULT 61.0,

    -- Index value (if computed)
    fear_index_value DECIMAL(5,2),
    fear_index_trend TEXT, -- 'rising', 'stable', 'falling'

    -- Survey source
    survey_source TEXT DEFAULT 'American Banker',
    survey_date DATE,

    -- Has new data
    has_new_survey_data BOOLEAN DEFAULT false,

    -- Rendered content
    header_text TEXT NOT NULL,
    body_html TEXT,

    -- Timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fear_index_run ON fault_watch_banker_fear_index (run_id);
CREATE INDEX IF NOT EXISTS idx_fear_index_generated ON fault_watch_banker_fear_index (generated_at_utc DESC);

-- ============================================
-- TABLE: fault_watch_net_assessments
-- Net Assessment Synthesis Block (8.5)
-- ============================================
CREATE TABLE IF NOT EXISTS fault_watch_net_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES fault_watch_parameter_runs(run_id) ON DELETE CASCADE,

    -- Component summaries (from other blocks)
    silver_summary TEXT,
    silver_price DECIMAL(10,2),
    silver_vs_danger_zone TEXT,

    ms_insider_summary TEXT,
    ms_insider_90d_value DECIMAL(15,2),
    ms_insider_buys_count INTEGER DEFAULT 0,

    fdic_summary TEXT,
    fdic_ytd_failures INTEGER,
    unrealized_losses_billions DECIMAL(10,2),

    flagstar_summary TEXT,
    flagstar_cre_ratio DECIMAL(6,1),

    bank_selloff_summary TEXT,

    -- Overall assessment
    conditions_vs_prior TEXT, -- 'improved', 'unchanged', 'worsened'
    systemic_risk_level TEXT, -- 'low', 'moderate', 'elevated', 'high', 'critical'

    -- Rendered synthesis
    assessment_text TEXT NOT NULL,
    status_line TEXT NOT NULL,
    -- Example: "NET ASSESSMENT as of 2026-02-03 15:00 EST: Silver bouncing from $76 → $89..."

    -- Full timestamps
    generated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generated_at_est TEXT NOT NULL,

    -- Prior run comparison
    prior_run_id UUID,
    prior_assessment_id UUID,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_net_assessment_run ON fault_watch_net_assessments (run_id);
CREATE INDEX IF NOT EXISTS idx_net_assessment_generated ON fault_watch_net_assessments (generated_at_utc DESC);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

ALTER TABLE fault_watch_fdic_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_ms_insider_tracker ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_flagstar_cre ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_silver_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_bank_selloff ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_banker_fear_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE fault_watch_net_assessments ENABLE ROW LEVEL SECURITY;

-- Public read access (these are displayed on the site)
CREATE POLICY "Public read access" ON fault_watch_fdic_status FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_ms_insider_tracker FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_flagstar_cre FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_silver_status FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_bank_selloff FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_banker_fear_index FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fault_watch_net_assessments FOR SELECT TO anon, authenticated USING (true);

-- Service role full access
CREATE POLICY "Service role full access" ON fault_watch_fdic_status FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_ms_insider_tracker FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_flagstar_cre FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_silver_status FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_bank_selloff FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_banker_fear_index FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON fault_watch_net_assessments FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================
-- VIEWS: Latest blocks for frontend
-- ============================================

-- Latest FDIC status
CREATE OR REPLACE VIEW fault_watch_latest_fdic AS
SELECT * FROM fault_watch_fdic_status
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest MS insider tracker
CREATE OR REPLACE VIEW fault_watch_latest_ms_insider AS
SELECT * FROM fault_watch_ms_insider_tracker
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest Flagstar CRE
CREATE OR REPLACE VIEW fault_watch_latest_flagstar AS
SELECT * FROM fault_watch_flagstar_cre
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest Silver status
CREATE OR REPLACE VIEW fault_watch_latest_silver AS
SELECT * FROM fault_watch_silver_status
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest Bank selloff
CREATE OR REPLACE VIEW fault_watch_latest_bank_selloff AS
SELECT * FROM fault_watch_bank_selloff
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest Banker Fear Index
CREATE OR REPLACE VIEW fault_watch_latest_fear_index AS
SELECT * FROM fault_watch_banker_fear_index
ORDER BY generated_at_utc DESC LIMIT 1;

-- Latest Net Assessment
CREATE OR REPLACE VIEW fault_watch_latest_net_assessment AS
SELECT * FROM fault_watch_net_assessments
ORDER BY generated_at_utc DESC LIMIT 1;

-- Combined dashboard view with all latest blocks
CREATE OR REPLACE VIEW fault_watch_narrative_dashboard AS
SELECT
    (SELECT row_to_json(f) FROM fault_watch_latest_fdic f) as fdic_status,
    (SELECT row_to_json(m) FROM fault_watch_latest_ms_insider m) as ms_insider,
    (SELECT row_to_json(fl) FROM fault_watch_latest_flagstar fl) as flagstar_cre,
    (SELECT row_to_json(s) FROM fault_watch_latest_silver s) as silver_status,
    (SELECT row_to_json(b) FROM fault_watch_latest_bank_selloff b) as bank_selloff,
    (SELECT row_to_json(fi) FROM fault_watch_latest_fear_index fi) as banker_fear_index,
    (SELECT row_to_json(n) FROM fault_watch_latest_net_assessment n) as net_assessment;

-- ============================================
-- FUNCTION: Get intraday history for a block
-- ============================================

CREATE OR REPLACE FUNCTION get_narrative_history(
    block_type TEXT,
    lookback_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
    id UUID,
    generated_at_utc TIMESTAMPTZ,
    generated_at_est TEXT,
    header_text TEXT,
    body_html TEXT
) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT id, generated_at_utc, generated_at_est, header_text, body_html
         FROM fault_watch_%s
         WHERE generated_at_utc >= NOW() - INTERVAL ''%s hours''
         ORDER BY generated_at_utc DESC',
        block_type,
        lookback_hours
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DONE!
-- ============================================
-- Run this SQL in Supabase SQL Editor after the main parameter search schema.
-- These tables store the core narrative blocks that update hourly.
