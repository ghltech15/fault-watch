-- Migration 005: Daily Scores Table
-- Computed risk scores per entity per day

-- Scores table (computed daily projections from events)
CREATE TABLE scores_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    entity_id UUID REFERENCES entities(id),
    -- Three-score system (0-100 each)
    funding_stress FLOAT CHECK (funding_stress BETWEEN 0 AND 100),
    enforcement_heat FLOAT CHECK (enforcement_heat BETWEEN 0 AND 100),
    deliverability_stress FLOAT CHECK (deliverability_stress BETWEEN 0 AND 100),
    -- Composite risk (0-10)
    composite_risk FLOAT CHECK (composite_risk BETWEEN 0 AND 10),
    -- Cascade detection
    cascade_triggered BOOLEAN DEFAULT false,
    -- Explainability
    explain_json JSONB DEFAULT '{}',
    -- Metadata
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- One score per entity per day
    UNIQUE(date, entity_id)
);

-- Indexes
CREATE INDEX idx_scores_date ON scores_daily(date DESC);
CREATE INDEX idx_scores_entity ON scores_daily(entity_id, date DESC);
CREATE INDEX idx_scores_composite ON scores_daily(composite_risk DESC);
CREATE INDEX idx_scores_cascade ON scores_daily(date DESC) WHERE cascade_triggered = true;

-- Market-wide scores (no specific entity)
CREATE TABLE scores_market (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    -- Aggregate market scores
    overall_risk FLOAT CHECK (overall_risk BETWEEN 0 AND 10),
    funding_stress_avg FLOAT,
    enforcement_heat_avg FLOAT,
    deliverability_stress_avg FLOAT,
    -- Banks in stress
    banks_in_stress INT DEFAULT 0,
    banks_in_danger INT DEFAULT 0,
    banks_in_crisis INT DEFAULT 0,
    -- Cascade status
    cascade_stage INT DEFAULT 0,  -- 0-5
    cascade_description TEXT,
    -- Raw indicator values (for debugging)
    indicators JSONB DEFAULT '{}',
    -- Timestamps
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scores_market_date ON scores_market(date DESC);

-- Risk label thresholds (reference table)
CREATE TABLE risk_labels (
    id SERIAL PRIMARY KEY,
    min_score FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    label VARCHAR(50) NOT NULL,
    color VARCHAR(20) NOT NULL,
    description TEXT
);

-- Seed risk labels
INSERT INTO risk_labels (min_score, max_score, label, color, description) VALUES
    (0.0, 1.5, 'STABLE', 'green', 'Normal market conditions'),
    (1.5, 2.5, 'MONITOR', 'blue', 'Elevated awareness, no action needed'),
    (2.5, 4.0, 'WATCH', 'yellow', 'Early warning signals present'),
    (4.0, 6.0, 'WARNING', 'orange', 'Significant stress indicators'),
    (6.0, 8.0, 'DANGER', 'red', 'Multiple stress vectors converging'),
    (8.0, 10.0, 'CRISIS', 'darkred', 'Imminent systemic risk');

-- View for latest entity scores
CREATE VIEW latest_entity_scores AS
SELECT DISTINCT ON (entity_id)
    sd.*,
    e.name as entity_name,
    e.entity_type,
    e.tickers,
    rl.label as risk_label,
    rl.color as risk_color
FROM scores_daily sd
JOIN entities e ON sd.entity_id = e.id
LEFT JOIN risk_labels rl ON sd.composite_risk >= rl.min_score AND sd.composite_risk < rl.max_score
ORDER BY entity_id, date DESC;

-- View for latest market score
CREATE VIEW latest_market_score AS
SELECT
    sm.*,
    rl.label as risk_label,
    rl.color as risk_color
FROM scores_market sm
LEFT JOIN risk_labels rl ON sm.overall_risk >= rl.min_score AND sm.overall_risk < rl.max_score
ORDER BY date DESC
LIMIT 1;

-- Function to get risk label for a score
CREATE OR REPLACE FUNCTION get_risk_label(score FLOAT)
RETURNS TABLE(label VARCHAR, color VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT rl.label, rl.color
    FROM risk_labels rl
    WHERE score >= rl.min_score AND score < rl.max_score
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to compute cascade stage from three scores
CREATE OR REPLACE FUNCTION compute_cascade_stage(
    funding FLOAT,
    enforcement FLOAT,
    deliverability FLOAT
) RETURNS INT AS $$
DECLARE
    high_count INT;
    extreme_count INT;
BEGIN
    -- Normalize to 0-10 scale
    funding := funding / 10;
    enforcement := enforcement / 10;
    deliverability := deliverability / 10;

    -- Count high (>=5) and extreme (>=7) scores
    high_count := (CASE WHEN funding >= 5 THEN 1 ELSE 0 END) +
                  (CASE WHEN enforcement >= 5 THEN 1 ELSE 0 END) +
                  (CASE WHEN deliverability >= 5 THEN 1 ELSE 0 END);

    extreme_count := (CASE WHEN funding >= 7 THEN 1 ELSE 0 END) +
                     (CASE WHEN enforcement >= 7 THEN 1 ELSE 0 END) +
                     (CASE WHEN deliverability >= 7 THEN 1 ELSE 0 END);

    -- Cascade stages
    IF extreme_count >= 2 THEN
        RETURN 5;  -- Full cascade
    ELSIF extreme_count = 1 AND high_count >= 2 THEN
        RETURN 4;  -- Cascade accelerating
    ELSIF high_count >= 2 THEN
        RETURN 3;  -- Cascade triggered
    ELSIF high_count = 1 THEN
        RETURN 2;  -- Stress emerging
    ELSIF funding > 3 OR enforcement > 3 OR deliverability > 3 THEN
        RETURN 1;  -- Early warning
    ELSE
        RETURN 0;  -- Normal
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE scores_daily IS 'Computed risk scores per entity per day';
COMMENT ON TABLE scores_market IS 'Aggregate market-wide risk scores per day';
COMMENT ON TABLE risk_labels IS 'Risk label thresholds and colors';
COMMENT ON COLUMN scores_daily.explain_json IS 'Score drivers: {funding_drivers: [], enforcement_drivers: [], deliverability_drivers: []}';
