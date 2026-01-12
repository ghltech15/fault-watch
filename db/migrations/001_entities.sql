-- Migration 001: Entities Table
-- Stores banks, regulators, metals, tickers, and persons

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Entity types enum
CREATE TYPE entity_type AS ENUM (
    'bank',
    'regulator',
    'metal',
    'ticker',
    'person',
    'exchange',
    'etf'
);

-- Entities table
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type entity_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    -- Identifiers
    cik VARCHAR(20),           -- SEC Central Index Key
    lei VARCHAR(50),           -- Legal Entity Identifier
    tickers TEXT[] DEFAULT '{}',
    -- Metadata
    domain VARCHAR(255),       -- Company website domain
    country VARCHAR(50),
    sector VARCHAR(100),
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_cik ON entities(cik) WHERE cik IS NOT NULL;
CREATE INDEX idx_entities_lei ON entities(lei) WHERE lei IS NOT NULL;
CREATE INDEX idx_entities_tickers ON entities USING GIN(tickers);
CREATE INDEX idx_entities_aliases ON entities USING GIN(aliases);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Seed initial entities (major banks and metals)
INSERT INTO entities (entity_type, name, aliases, cik, tickers) VALUES
    -- Major banks with silver exposure
    ('bank', 'JPMorgan Chase & Co.', ARRAY['JPM', 'JPMorgan', 'JP Morgan'], '0000019617', ARRAY['JPM']),
    ('bank', 'Citigroup Inc.', ARRAY['Citi', 'Citibank'], '0000831001', ARRAY['C']),
    ('bank', 'Bank of America Corporation', ARRAY['BofA', 'BoA'], '0000070858', ARRAY['BAC']),
    ('bank', 'Morgan Stanley', ARRAY['MS'], '0000895421', ARRAY['MS']),
    ('bank', 'Goldman Sachs Group Inc.', ARRAY['Goldman', 'GS'], '0000886982', ARRAY['GS']),
    ('bank', 'Wells Fargo & Company', ARRAY['Wells'], '0000072971', ARRAY['WFC']),
    ('bank', 'UBS Group AG', ARRAY['UBS'], '0001610520', ARRAY['UBS']),
    ('bank', 'Credit Suisse Group AG', ARRAY['CS', 'Credit Suisse'], '0001159510', ARRAY['CS']),
    ('bank', 'HSBC Holdings plc', ARRAY['HSBC'], '0001089113', ARRAY['HSBC']),
    ('bank', 'Barclays PLC', ARRAY['Barclays'], '0000312069', ARRAY['BCS']),
    -- Metals
    ('metal', 'Silver', ARRAY['Ag', 'XAG'], NULL, ARRAY['SI=F', 'SLV']),
    ('metal', 'Gold', ARRAY['Au', 'XAU'], NULL, ARRAY['GC=F', 'GLD']),
    ('metal', 'Platinum', ARRAY['Pt', 'XPT'], NULL, ARRAY['PL=F']),
    ('metal', 'Palladium', ARRAY['Pd', 'XPD'], NULL, ARRAY['PA=F']),
    -- Regulators
    ('regulator', 'Securities and Exchange Commission', ARRAY['SEC'], NULL, NULL),
    ('regulator', 'Commodity Futures Trading Commission', ARRAY['CFTC'], NULL, NULL),
    ('regulator', 'Office of the Comptroller of the Currency', ARRAY['OCC'], NULL, NULL),
    ('regulator', 'Federal Deposit Insurance Corporation', ARRAY['FDIC'], NULL, NULL),
    ('regulator', 'Federal Reserve System', ARRAY['Fed', 'Federal Reserve'], NULL, NULL),
    ('regulator', 'Financial Conduct Authority', ARRAY['FCA'], NULL, NULL),
    -- Exchanges
    ('exchange', 'COMEX', ARRAY['CME COMEX', 'Comex'], NULL, NULL),
    ('exchange', 'London Bullion Market Association', ARRAY['LBMA'], NULL, NULL),
    ('exchange', 'Shanghai Gold Exchange', ARRAY['SGE'], NULL, NULL);

-- Comments
COMMENT ON TABLE entities IS 'Master entity table for banks, regulators, metals, and other tracked entities';
COMMENT ON COLUMN entities.cik IS 'SEC Central Index Key for US-registered entities';
COMMENT ON COLUMN entities.lei IS 'Legal Entity Identifier (ISO 17442)';
