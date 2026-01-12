-- Migration 002: Sources Table
-- Defines data sources with their trust tiers

-- Source type enum
CREATE TYPE source_type AS ENUM (
    'rss',          -- RSS/Atom feeds
    'api',          -- REST/GraphQL APIs
    'scrape',       -- Web scraping
    'manual',       -- Manual data entry
    'filing'        -- Regulatory filings (SEC EDGAR, etc.)
);

-- Trust tier enum (1 = highest trust)
CREATE TYPE trust_tier AS ENUM (
    '1',  -- Official: SEC, CFTC, OCC, FDIC, Fed, Courts
    '2',  -- Credible: Reuters, Bloomberg, WSJ, FT
    '3'   -- Social: Reddit, Twitter, TikTok, Blogs
);

-- Sources table
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type source_type NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    base_url TEXT,
    trust_tier trust_tier NOT NULL,
    -- Configuration for collector
    config JSONB DEFAULT '{}',
    -- Status
    active BOOLEAN DEFAULT true,
    last_successful_fetch TIMESTAMPTZ,
    consecutive_failures INT DEFAULT 0,
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sources_trust_tier ON sources(trust_tier);
CREATE INDEX idx_sources_active ON sources(active);
CREATE INDEX idx_sources_type ON sources(source_type);

-- Trigger for updated_at
CREATE TRIGGER update_sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Seed Tier 1 sources (Official)
INSERT INTO sources (source_type, name, base_url, trust_tier, config) VALUES
    ('filing', 'SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar', '1', '{"rate_limit_ms": 100}'::jsonb),
    ('filing', 'SEC Enforcement', 'https://www.sec.gov/litigation/litreleases.htm', '1', '{}'::jsonb),
    ('filing', 'SEC Whistleblower', 'https://www.sec.gov/whistleblower', '1', '{}'::jsonb),
    ('api', 'CFTC Enforcement', 'https://www.cftc.gov/PressRoom/PressReleases', '1', '{}'::jsonb),
    ('scrape', 'OCC Enforcement', 'https://www.occ.gov/topics/laws-and-regulations/enforcement-actions', '1', '{}'::jsonb),
    ('scrape', 'FDIC Bank Failures', 'https://www.fdic.gov/resources/resolutions/bank-failures', '1', '{}'::jsonb),
    ('api', 'Fed H.4.1', 'https://www.federalreserve.gov/releases/h41', '1', '{}'::jsonb),
    ('api', 'FRED', 'https://api.stlouisfed.org/fred', '1', '{"requires_key": true}'::jsonb),
    ('api', 'CME COMEX', 'https://www.cmegroup.com/markets/metals', '1', '{}'::jsonb);

-- Seed Tier 2 sources (Credible Press)
INSERT INTO sources (source_type, name, base_url, trust_tier, config) VALUES
    ('rss', 'Reuters Finance', 'https://www.reuters.com/news/archive/businessNews', '2', '{}'::jsonb),
    ('rss', 'Bloomberg Markets', 'https://www.bloomberg.com/markets', '2', '{}'::jsonb),
    ('rss', 'Wall Street Journal', 'https://www.wsj.com', '2', '{}'::jsonb),
    ('rss', 'Financial Times', 'https://www.ft.com', '2', '{}'::jsonb),
    ('rss', 'Kitco News', 'https://www.kitco.com/news', '2', '{}'::jsonb),
    ('api', 'Finnhub', 'https://finnhub.io/api', '2', '{"requires_key": true}'::jsonb);

-- Seed Tier 3 sources (Social)
INSERT INTO sources (source_type, name, base_url, trust_tier, config) VALUES
    ('api', 'Reddit WSS', 'https://reddit.com/r/wallstreetsilver', '3', '{"subreddit": "wallstreetsilver"}'::jsonb),
    ('api', 'Reddit Silverbugs', 'https://reddit.com/r/silverbugs', '3', '{"subreddit": "silverbugs"}'::jsonb),
    ('api', 'Reddit Gold', 'https://reddit.com/r/gold', '3', '{"subreddit": "gold"}'::jsonb),
    ('scrape', 'ZeroHedge', 'https://www.zerohedge.com', '3', '{}'::jsonb),
    ('scrape', 'SilverSeek', 'https://www.silverseek.com', '3', '{}'::jsonb);

-- Dealer sources (Tier 2 - real prices but commercial)
INSERT INTO sources (source_type, name, base_url, trust_tier, config) VALUES
    ('scrape', 'JM Bullion', 'https://www.jmbullion.com', '2', '{}'::jsonb),
    ('scrape', 'APMEX', 'https://www.apmex.com', '2', '{}'::jsonb),
    ('scrape', 'SD Bullion', 'https://www.sdbullion.com', '2', '{}'::jsonb);

-- Comments
COMMENT ON TABLE sources IS 'Data sources with trust tier classification';
COMMENT ON COLUMN sources.trust_tier IS 'Trust level: 1=Official, 2=Credible Press, 3=Social';
COMMENT ON COLUMN sources.config IS 'Source-specific configuration (rate limits, API keys, etc.)';
