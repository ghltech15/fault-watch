-- Migration 003: Events Table
-- Append-only event store for verified facts from Tier 1/2 sources

-- Event type enum (extensible via ALTER TYPE)
CREATE TYPE event_type AS ENUM (
    -- Regulatory actions
    'regulator_action',      -- SEC/CFTC/OCC enforcement
    'wells_notice',          -- Warning of upcoming enforcement
    'settlement',            -- Agreed resolution
    'consent_order',         -- Formal agreement
    'cease_desist',          -- Stop order
    'criminal_referral',     -- DOJ referral
    'penalty',               -- Civil money penalty
    'covered_action',        -- SEC whistleblower covered action
    -- Bank events
    'bank_failure',          -- FDIC bank failure
    'bank_merger',           -- Bank M&A
    'bank_downgrade',        -- Credit rating downgrade
    'bank_earnings',         -- Quarterly earnings
    -- Fed/Treasury
    'fed_balance_sheet',     -- H.4.1 release
    'fed_rate_decision',     -- FOMC decision
    'treasury_auction',      -- Bond auction
    -- COMEX/Market
    'comex_inventory',       -- Warehouse stock update
    'comex_delivery',        -- Delivery notice
    'price_move',            -- Significant price movement
    -- Filings
    'sec_filing',            -- 10-K, 10-Q, 8-K, Form 4
    'cot_report',            -- CFTC COT data
    -- News (from Tier 2)
    'news_article',          -- Breaking news from credible source
    -- Other
    'custom'                 -- For extensibility
);

-- Events table (append-only)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type event_type NOT NULL,
    -- References
    entity_id UUID REFERENCES entities(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    -- Timestamps
    published_at TIMESTAMPTZ,        -- When source published
    observed_at TIMESTAMPTZ DEFAULT NOW(),  -- When we captured
    -- Payload
    payload JSONB NOT NULL,
    -- Deduplication
    hash VARCHAR(64) UNIQUE,  -- SHA256 for content-based dedupe
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Note: No updated_at - events are immutable once created

-- Indexes for common query patterns
CREATE INDEX idx_events_entity ON events(entity_id, observed_at DESC);
CREATE INDEX idx_events_type ON events(event_type, observed_at DESC);
CREATE INDEX idx_events_source ON events(source_id, observed_at DESC);
CREATE INDEX idx_events_published ON events(published_at DESC) WHERE published_at IS NOT NULL;
CREATE INDEX idx_events_payload ON events USING GIN(payload);

-- Partitioning hint: For production with high volume, consider partitioning by month:
-- CREATE TABLE events (...) PARTITION BY RANGE (observed_at);

-- View for recent events (last 7 days)
CREATE VIEW recent_events AS
SELECT
    e.*,
    ent.name as entity_name,
    ent.entity_type,
    s.name as source_name,
    s.trust_tier
FROM events e
LEFT JOIN entities ent ON e.entity_id = ent.id
JOIN sources s ON e.source_id = s.id
WHERE e.observed_at > NOW() - INTERVAL '7 days'
ORDER BY e.observed_at DESC;

-- View for regulatory actions
CREATE VIEW regulatory_events AS
SELECT
    e.*,
    ent.name as entity_name,
    ent.tickers,
    s.name as source_name
FROM events e
LEFT JOIN entities ent ON e.entity_id = ent.id
JOIN sources s ON e.source_id = s.id
WHERE e.event_type IN (
    'regulator_action', 'wells_notice', 'settlement',
    'consent_order', 'cease_desist', 'criminal_referral', 'penalty'
)
ORDER BY e.observed_at DESC;

-- Comments
COMMENT ON TABLE events IS 'Append-only event store for verified facts from trusted sources';
COMMENT ON COLUMN events.hash IS 'SHA256 hash for content-based deduplication';
COMMENT ON COLUMN events.published_at IS 'When the source originally published (may be NULL)';
COMMENT ON COLUMN events.observed_at IS 'When fault.watch captured the event';
