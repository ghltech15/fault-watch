-- Migration 004: Claims and Corroborations
-- Stores unverified assertions from Tier 3 sources with graduation tracking

-- Claim type enum
CREATE TYPE claim_type AS ENUM (
    'nationalization',   -- Bank nationalization/bailout claims
    'investigation',     -- Regulatory investigation claims
    'liquidity',         -- Bank run/liquidity crisis claims
    'delivery',          -- Delivery failure/default claims
    'fraud',             -- Fraud/manipulation claims
    'insider',           -- Insider trading/knowledge claims
    'price_target',      -- Price prediction claims
    'other'              -- Catch-all
);

-- Claim status enum (lifecycle)
CREATE TYPE claim_status AS ENUM (
    'new',              -- Just captured, not yet triaged
    'triage',           -- Being evaluated
    'corroborating',    -- Actively searching for Tier 1 confirmation
    'confirmed',        -- Corroborated by Tier 1 event
    'debunked',         -- Contradicted by Tier 1 evidence
    'stale'             -- No corroboration after timeout (7 days)
);

-- Claims table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- References
    entity_id UUID REFERENCES entities(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    -- Content
    claim_text TEXT NOT NULL,
    claim_type claim_type NOT NULL,
    -- Source attribution
    url TEXT,
    author VARCHAR(255),
    -- Engagement metrics (for credibility)
    engagement INT DEFAULT 0,  -- upvotes, likes, etc.
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    -- Credibility assessment
    credibility_score INT CHECK (credibility_score BETWEEN 0 AND 100),
    credibility_factors JSONB DEFAULT '{}',  -- Breakdown of scoring
    -- Status lifecycle
    status claim_status DEFAULT 'new',
    status_changed_at TIMESTAMPTZ DEFAULT NOW(),
    status_reason TEXT,  -- Why status changed
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_claims_entity ON claims(entity_id, created_at DESC);
CREATE INDEX idx_claims_status ON claims(status, created_at DESC);
CREATE INDEX idx_claims_type ON claims(claim_type, created_at DESC);
CREATE INDEX idx_claims_credibility ON claims(credibility_score DESC) WHERE credibility_score IS NOT NULL;
CREATE INDEX idx_claims_source ON claims(source_id, created_at DESC);

-- Trigger to update status_changed_at
CREATE OR REPLACE FUNCTION update_claim_status_changed()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        NEW.status_changed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_claims_status_changed
    BEFORE UPDATE ON claims
    FOR EACH ROW
    EXECUTE FUNCTION update_claim_status_changed();

-- Corroborations table (links Claims to Events)
CREATE TABLE corroborations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    -- Match quality
    match_confidence FLOAT CHECK (match_confidence BETWEEN 0 AND 1),
    match_reason TEXT,  -- Why this event corroborates the claim
    -- Who/what made the match
    matched_by VARCHAR(50) DEFAULT 'auto',  -- auto|manual|ml
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Prevent duplicate corroborations
    UNIQUE(claim_id, event_id)
);

-- Indexes
CREATE INDEX idx_corroborations_claim ON corroborations(claim_id);
CREATE INDEX idx_corroborations_event ON corroborations(event_id);

-- View for claims awaiting triage
CREATE VIEW claims_triage_queue AS
SELECT
    c.*,
    ent.name as entity_name,
    s.name as source_name,
    (SELECT COUNT(*) FROM corroborations cor WHERE cor.claim_id = c.id) as corroboration_count
FROM claims c
LEFT JOIN entities ent ON c.entity_id = ent.id
JOIN sources s ON c.source_id = s.id
WHERE c.status IN ('new', 'triage')
ORDER BY c.credibility_score DESC NULLS LAST, c.created_at DESC;

-- View for confirmed claims
CREATE VIEW confirmed_claims AS
SELECT
    c.*,
    ent.name as entity_name,
    s.name as source_name,
    cor.event_id as confirming_event_id,
    cor.match_confidence
FROM claims c
LEFT JOIN entities ent ON c.entity_id = ent.id
JOIN sources s ON c.source_id = s.id
JOIN corroborations cor ON c.id = cor.claim_id
WHERE c.status = 'confirmed'
ORDER BY c.status_changed_at DESC;

-- Function to graduate stale claims
CREATE OR REPLACE FUNCTION graduate_stale_claims()
RETURNS INT AS $$
DECLARE
    updated_count INT;
BEGIN
    UPDATE claims
    SET status = 'stale', status_reason = 'No corroboration within 7 days'
    WHERE status IN ('new', 'triage', 'corroborating')
      AND created_at < NOW() - INTERVAL '7 days';

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE claims IS 'Unverified assertions from Tier 3 sources (social media, blogs)';
COMMENT ON TABLE corroborations IS 'Links claims to confirming Tier 1 events';
COMMENT ON COLUMN claims.credibility_score IS 'Computed credibility (0-100): account age, history, engagement, etc.';
COMMENT ON COLUMN claims.status IS 'Lifecycle: new → triage → corroborating → confirmed/debunked/stale';
