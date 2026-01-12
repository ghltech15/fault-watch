-- ============================================
-- fault.watch - Supabase Database Schema
-- ============================================
-- Run this in your Supabase SQL Editor
-- Project URL: https://app.supabase.com/project/YOUR_PROJECT/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: current_prices
-- Stores latest prices for dashboard
-- ============================================
CREATE TABLE IF NOT EXISTS current_prices (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(18,4) NOT NULL,
    prev_close DECIMAL(18,4),
    change_pct DECIMAL(8,4),
    week_change DECIMAL(8,4),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default symbols
INSERT INTO current_prices (symbol, name, price) VALUES
    ('SI=F', 'Silver Futures', 80.00),
    ('GC=F', 'Gold Futures', 4520.00),
    ('MS', 'Morgan Stanley', 135.00),
    ('JPM', 'JPMorgan Chase', 250.00),
    ('C', 'Citigroup', 75.00),
    ('BAC', 'Bank of America', 45.00),
    ('GS', 'Goldman Sachs', 580.00),
    ('^VIX', 'VIX Index', 15.00),
    ('DX-Y.NYB', 'Dollar Index', 102.00),
    ('GDX', 'Gold Miners ETF', 45.00),
    ('SILJ', 'Silver Miners ETF', 18.00),
    ('SLV', 'Silver ETF', 72.00),
    ('KRE', 'Regional Banks ETF', 55.00),
    ('HYG', 'High Yield ETF', 77.00),
    ('SPY', 'S&P 500 ETF', 600.00),
    ('TLT', 'Long Treasury ETF', 92.00)
ON CONFLICT (symbol) DO NOTHING;

-- ============================================
-- TABLE: price_history
-- Historical price data for charts
-- ============================================
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(18,4) NOT NULL,
    change_pct DECIMAL(8,4),
    volume BIGINT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_price_history_symbol_time 
    ON price_history (symbol, recorded_at DESC);

-- ============================================
-- TABLE: user_positions
-- User's tracked positions
-- ============================================
CREATE TABLE IF NOT EXISTS user_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    position_type VARCHAR(20) NOT NULL, -- 'call', 'put', 'stock', 'physical'
    strike DECIMAL(10,2),
    expiration DATE,
    contracts INTEGER,
    shares INTEGER,
    ounces DECIMAL(10,2),
    cost_basis DECIMAL(12,2),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user queries
CREATE INDEX IF NOT EXISTS idx_positions_user 
    ON user_positions (user_id, is_active);

-- ============================================
-- TABLE: user_alerts
-- Custom price alerts
-- ============================================
CREATE TABLE IF NOT EXISTS user_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(20) NOT NULL, -- 'price_above', 'price_below', 'change_pct'
    threshold DECIMAL(18,4) NOT NULL,
    message TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for active alerts
CREATE INDEX IF NOT EXISTS idx_alerts_active 
    ON user_alerts (is_active, symbol);

-- ============================================
-- TABLE: fed_repo_data
-- Federal Reserve repo operations
-- ============================================
CREATE TABLE IF NOT EXISTS fed_repo_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    amount_billions DECIMAL(10,2),
    operation_type VARCHAR(50),
    notes TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert known data
INSERT INTO fed_repo_data (date, amount_billions, notes) VALUES
    ('2025-12-27', 17.25, 'Silver spike to $83 - emergency repo'),
    ('2025-12-30', 5.80, 'Continued stress'),
    ('2025-12-31', 0, 'Holiday - no operations')
ON CONFLICT (date) DO NOTHING;

-- ============================================
-- TABLE: bank_exposure
-- Bank PM derivatives exposure (from OCC)
-- ============================================
CREATE TABLE IF NOT EXISTS bank_exposure (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pm_derivatives_billions DECIMAL(10,2),
    equity_billions DECIMAL(10,2),
    pct_of_total DECIMAL(5,2),
    risk_tier INTEGER, -- 1=extreme, 2=high, 3=moderate
    notes TEXT,
    data_source VARCHAR(100),
    report_date DATE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert OCC Q3 2025 data
INSERT INTO bank_exposure (ticker, name, pm_derivatives_billions, equity_billions, pct_of_total, risk_tier, notes, data_source, report_date) VALUES
    ('JPM', 'JPMorgan Chase', 437.4, 330, 62.1, 1, 'Largest PM derivatives holder, SLV custodian', 'OCC Q3 2025', '2025-09-30'),
    ('C', 'Citigroup', 204.3, 175, 29.0, 1, 'Second largest, weakest balance sheet', 'OCC Q3 2025', '2025-09-30'),
    ('MS', 'Morgan Stanley', NULL, 100, NULL, 1, 'Not in OCC Top 4 - Hidden exposure, rumored 5.9B oz short', 'Whistleblower', '2026-01-07'),
    ('BAC', 'Bank of America', 47.9, 280, 6.8, 2, 'Third largest', 'OCC Q3 2025', '2025-09-30'),
    ('GS', 'Goldman Sachs', 0.614, 120, 0.1, 3, 'Minimal reported exposure', 'OCC Q3 2025', '2025-09-30'),
    ('HSBC', 'HSBC Holdings', NULL, 190, NULL, 2, 'LBMA market maker - London exposure', 'LBMA', NULL),
    ('DB', 'Deutsche Bank', NULL, 55, NULL, 2, 'Settled PM manipulation 2016', 'DOJ Settlement', '2016-01-01'),
    ('UBS', 'UBS Group', NULL, 100, NULL, 2, '$15M CFTC fine 2018', 'CFTC', '2018-01-01'),
    ('BCS', 'Barclays', NULL, 50, NULL, 3, 'LBMA market maker', 'LBMA', NULL),
    ('BNS', 'Scotiabank', NULL, 65, NULL, 2, '$127M fine 2020 PM manipulation', 'DOJ/CFTC', '2020-01-01')
ON CONFLICT (ticker) DO UPDATE SET
    pm_derivatives_billions = EXCLUDED.pm_derivatives_billions,
    updated_at = NOW();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Users can only see/edit their own data
-- ============================================

-- Enable RLS
ALTER TABLE user_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;

-- Positions policies
CREATE POLICY "Users can view own positions" ON user_positions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own positions" ON user_positions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own positions" ON user_positions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own positions" ON user_positions
    FOR DELETE USING (auth.uid() = user_id);

-- Alerts policies
CREATE POLICY "Users can view own alerts" ON user_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alerts" ON user_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own alerts" ON user_alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own alerts" ON user_alerts
    FOR DELETE USING (auth.uid() = user_id);

-- Public read access for reference tables
ALTER TABLE current_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_exposure ENABLE ROW LEVEL SECURITY;
ALTER TABLE fed_repo_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access" ON current_prices FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON bank_exposure FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read access" ON fed_repo_data FOR SELECT TO anon, authenticated USING (true);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to update timestamp on row update
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_positions_timestamp
    BEFORE UPDATE ON user_positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_prices_timestamp
    BEFORE UPDATE ON current_prices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- REALTIME SUBSCRIPTIONS
-- Enable realtime for live updates
-- ============================================

-- Enable realtime for current prices (dashboard updates)
ALTER PUBLICATION supabase_realtime ADD TABLE current_prices;

-- Enable realtime for user alerts (trigger notifications)
ALTER PUBLICATION supabase_realtime ADD TABLE user_alerts;

-- ============================================
-- VIEWS
-- ============================================

-- View: Dashboard summary
CREATE OR REPLACE VIEW dashboard_summary AS
SELECT 
    (SELECT price FROM current_prices WHERE symbol = 'SI=F') as silver_price,
    (SELECT price FROM current_prices WHERE symbol = 'GC=F') as gold_price,
    (SELECT price FROM current_prices WHERE symbol = 'MS') as ms_price,
    (SELECT price FROM current_prices WHERE symbol = '^VIX') as vix,
    (SELECT SUM(amount_billions) FROM fed_repo_data WHERE date >= CURRENT_DATE - INTERVAL '7 days') as fed_repo_7d,
    (SELECT SUM(pm_derivatives_billions) FROM bank_exposure WHERE pm_derivatives_billions IS NOT NULL) as total_pm_derivatives;

-- ============================================
-- DONE!
-- ============================================
-- Your database is now ready for fault.watch
-- Next: Get your API keys from Supabase dashboard
