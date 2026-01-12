# Verification Policy

How fault.watch verifies information and prevents narrative contamination.

## Trust Tier System

### Tier 1: Official Sources (Creates Events)

These sources produce **verified facts** that are stored as Events:

| Source | Type | What We Capture |
|--------|------|-----------------|
| SEC EDGAR | Filings | 10-K, 10-Q, 8-K, Form 4 |
| SEC Enforcement | Actions | Wells notices, settlements, penalties |
| SEC Whistleblower | Awards | Covered actions |
| CFTC | Actions | Enforcement, COT reports |
| OCC | Actions | Bank enforcement orders |
| FDIC | Events | Bank failures, resolutions |
| Federal Reserve | Data | H.4.1, rate decisions |
| CME/COMEX | Data | Inventory, delivery notices |
| Courts | Records | Dockets, rulings |

**Rule**: Tier 1 data is treated as ground truth. Events from these sources are:
- Stored immediately as verified facts
- Never modified after creation
- Used to confirm or debunk claims

### Tier 2: Credible Press (Creates Events + Claims)

These sources produce **credible information** that creates both Events and Claims:

| Source | Type | Trust Level |
|--------|------|-------------|
| Reuters | Wire | High |
| Bloomberg | Wire | High |
| Wall Street Journal | News | High |
| Financial Times | News | High |
| Associated Press | Wire | High |
| Kitco News | Commodity | Medium-High |
| Finnhub | Data | Medium-High |

**Rule**: Tier 2 data is:
- Credible but not official
- Creates Events (for tracking)
- Also creates Claims (for cross-verification)
- Ideally confirmed by Tier 1 within 24-48 hours

### Tier 3: Social Sources (Creates Claims Only)

These sources produce **unverified assertions** that require verification:

| Source | Platform | Risk Level |
|--------|----------|------------|
| Reddit (WSS, Silverbugs) | Social | High hype |
| Twitter/X | Social | High noise |
| ZeroHedge | Alt-media | Medium hype |
| TikTok | Social | Very high hype |
| Blogs | Various | Varies |

**Rule**: Tier 3 data is:
- NEVER displayed as fact
- Always labeled as "UNVERIFIED CLAIM"
- Must be corroborated by Tier 1 to become fact
- Subject to credibility scoring

## Claim Lifecycle

```
        ┌──────────────┐
        │     new      │  Just captured
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │    triage    │  Being evaluated
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │ corroborating│  Searching for Tier 1 match
        └──────┬───────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼───────┐ ┌─────▼────────┐
│  confirmed   │ │   debunked   │
│  (Event!)    │ │  (Tier 1     │
└──────────────┘ │  contradicts)│
                 └──────────────┘
       │               │
       └───────┬───────┘
               │ (7 days, no match)
        ┌──────▼───────┐
        │    stale     │
        └──────────────┘
```

### Status Definitions

| Status | Meaning | Display |
|--------|---------|---------|
| `new` | Just captured, not evaluated | Yellow badge |
| `triage` | Being evaluated by system | Yellow badge |
| `corroborating` | Active search for Tier 1 match | Yellow badge |
| `confirmed` | Tier 1 event corroborates | Green badge |
| `debunked` | Tier 1 evidence contradicts | Red badge |
| `stale` | No corroboration after 7 days | Gray badge |

## Credibility Scoring

Claims receive a credibility score (0-100) based on:

### Positive Factors
| Factor | Points | Condition |
|--------|--------|-----------|
| Account age | +10 | >365 days |
| Account age | +5 | >90 days |
| High engagement | +15 | >1000 upvotes/likes |
| High engagement | +10 | >500 |
| High engagement | +5 | >100 |
| Cross-source corroboration | +20 | Same claim from 3+ sources in 24h |
| Cross-source corroboration | +10 | 2 sources |
| Has artifact | +15 | Screenshot of filing/document |
| Quality source | +10 | Known credible author |

### Negative Factors
| Factor | Points | Condition |
|--------|--------|-----------|
| New account | -10 | <30 days old |
| Absolute language | -15 | "guaranteed", "confirmed", "100%" |
| Known hoax pattern | -50 | Matches previous hoaxes |
| No source cited | -10 | No link or reference |

### Score Interpretation
| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | High credibility | Prioritize for verification |
| 60-79 | Medium credibility | Standard triage |
| 40-59 | Low credibility | Monitor only |
| 0-39 | Very low credibility | Likely noise |

## Corroboration Rules

### Automatic Confirmation
A claim is automatically confirmed when:
1. A Tier 1 event is observed
2. Entity matches (same bank, regulator, etc.)
3. Claim type matches event type
4. Timing is within 7 days

Example:
- Claim: "JPM under SEC investigation" (Reddit, Tier 3)
- Event: SEC files enforcement action against JPM (SEC EDGAR, Tier 1)
- Result: Claim status → `confirmed`, corroboration created

### Automatic Debunking
A claim is automatically debunked when:
1. A Tier 1 event directly contradicts
2. Or: Official statement denies claim
3. Or: Time-sensitive claim expires without evidence

Example:
- Claim: "COMEX will default tomorrow" (Reddit)
- Event: COMEX reports normal deliveries next day
- Result: Claim status → `debunked`

### Stale Claims
Claims become stale when:
- 7 days pass without Tier 1 corroboration
- No contradicting evidence either
- Claim is no longer actionable

## Display Rules

### NEVER Display as Fact
- Tier 3 claims that aren't confirmed
- Price predictions
- "Source says" without verification
- Screenshots without verification

### Always Label
```
┌─────────────────────────────────┐
│ ⚠️ UNVERIFIED CLAIM            │
│                                 │
│ "JPM under investigation..."    │
│                                 │
│ Source: r/wallstreetsilver      │
│ Credibility: 62/100             │
│ Status: corroborating           │
└─────────────────────────────────┘
```

### Confirmed Claims
```
┌─────────────────────────────────┐
│ ✓ CONFIRMED                     │
│                                 │
│ "JPM under investigation..."    │
│                                 │
│ Confirmed by: SEC Filing        │
│ Confidence: 95%                 │
└─────────────────────────────────┘
```

## Narrative Contamination Prevention

### Red Flags
We watch for and discount:
1. **Hype cycles**: Same claim repeated across social media
2. **Circular sourcing**: "Reuters reports ZeroHedge said..."
3. **Missing artifacts**: Claims without documentary evidence
4. **Timing manipulation**: Claims timed for market impact

### Quality Controls
1. **Deduplication**: Same claim from multiple Tier 3 sources counts as 1
2. **Source diversity**: Cross-source corroboration requires different platforms
3. **Velocity limits**: Rapid claim spikes trigger review
4. **Human review**: High-impact claims get manual verification

## API Display Guidelines

### For Frontend Developers

```typescript
// Always check claim status before display
function displayClaim(claim: Claim) {
  if (claim.status === 'confirmed') {
    return { label: 'CONFIRMED', color: 'green', icon: '✓' };
  } else if (claim.status === 'debunked') {
    return { label: 'DEBUNKED', color: 'red', icon: '✗' };
  } else if (claim.status === 'stale') {
    return { label: 'STALE', color: 'gray', icon: '○' };
  } else {
    // new, triage, corroborating
    return { label: 'UNVERIFIED', color: 'yellow', icon: '⚠' };
  }
}

// Never display Tier 3 as fact
function canDisplayAsFact(item: Event | Claim) {
  if ('claim_text' in item) {
    return item.status === 'confirmed';
  }
  return true; // Events are facts
}
```

### Risk Score Display
- Always show the source of risk drivers
- Never extrapolate beyond what data supports
- Show confidence intervals where available
