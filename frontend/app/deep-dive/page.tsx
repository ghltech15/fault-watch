'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  ArrowLeft,
  AlertTriangle,
  TrendingUp,
  Building2,
  Clock,
  DollarSign,
  Shield,
  FileText,
  Scale,
  Skull,
  Target,
  Calendar,
  BarChart3,
  Globe,
  BookOpen
} from 'lucide-react'

export default function DeepDivePage() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[var(--bg-primary)]/95 backdrop-blur-md border-b border-[var(--border-primary)]">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--text-muted)]">Last Updated: January 23, 2026</span>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative py-16 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-red-500/10 to-transparent" />
        <div className="max-w-4xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-amber-500/20 text-amber-400 px-4 py-2 rounded-full mb-6">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm font-bold">UNVERIFIED SPECULATIVE ANALYSIS</span>
            </div>
            <h1 className="text-4xl md:text-6xl font-black text-[var(--text-primary)] mb-4">
              THE SILVER SHORT<br />
              <span className="text-red-500">APOCALYPSE</span>
            </h1>
            <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto">
              Bank Insolvency Analysis - A comprehensive examination of the alleged silver short positions threatening global financial stability
            </p>
          </motion.div>
        </div>
      </section>

      {/* Unverified Notice */}
      <section className="max-w-4xl mx-auto px-4 mb-6">
        <div className="bg-amber-500/20 border-2 border-amber-500 rounded-xl p-6">
          <div className="flex items-center justify-center gap-3 text-amber-400 mb-3">
            <AlertTriangle className="w-6 h-6" />
            <span className="font-bold text-xl">UNVERIFIED ANALYSIS</span>
            <AlertTriangle className="w-6 h-6" />
          </div>
          <p className="text-center text-amber-200/80">
            The information in this report has NOT been independently verified. We are actively working to verify all claims and data points.
            This represents one possible scenario based on available information and should be treated as speculative analysis only.
          </p>
        </div>
      </section>

      {/* Legal Notice */}
      <section className="max-w-4xl mx-auto px-4 mb-6">
        <div className="bg-red-500/10 border-2 border-red-500/50 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <Scale className="w-8 h-8 text-red-400 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-red-400 text-lg mb-3">LEGAL NOTICE - NOT INVESTMENT ADVICE</h3>
              <div className="space-y-2 text-sm text-[var(--text-secondary)]">
                <p>
                  <strong className="text-[var(--text-primary)]">EDUCATIONAL PURPOSES ONLY:</strong> Nothing on this website constitutes financial,
                  investment, legal, or tax advice. The content is for informational and educational purposes only. We are not registered
                  investment advisors, broker-dealers, or financial planners.
                </p>
                <p>
                  <strong className="text-[var(--text-primary)]">EXPLORING POSSIBILITIES:</strong> This report explores potential scenarios and
                  "what if" analyses based on publicly available information, rumors, and mathematical modeling. We present these possibilities
                  to help readers understand potential market dynamics - these are NOT predictions of what will happen.
                </p>
                <p>
                  <strong className="text-[var(--text-primary)]">NO RECOMMENDATIONS:</strong> We do not recommend buying, selling, or holding any
                  securities, commodities, or financial instruments. Any decisions you make are solely your own responsibility.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="max-w-4xl mx-auto px-4 mb-12">
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-amber-400 mb-2">UNVERIFIED INFORMATION DISCLAIMER</h3>
              <div className="space-y-2 text-sm text-[var(--text-secondary)]">
                <p>
                  <strong className="text-amber-300">VERIFICATION STATUS:</strong> The data and claims in this report have NOT been independently
                  verified. We are continuously working to verify all information through multiple sources.
                </p>
                <p>
                  <strong className="text-amber-300">SOURCES:</strong> Information is compiled from publicly available data, leaked documents,
                  unverified rumors from financial sources, and mathematical modeling. Position sizes and entry prices cannot be independently
                  confirmed. All banks mentioned deny having problematic silver exposure.
                </p>
                <p>
                  <strong className="text-amber-300">YOUR RESPONSIBILITY:</strong> Always conduct your own due diligence. Consult with qualified
                  financial professionals before making any investment decisions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Executive Summary */}
      <Section
        icon={<FileText className="w-6 h-6" />}
        title="EXECUTIVE SUMMARY"
        id="executive-summary"
      >
        <div className="prose prose-invert max-w-none">
          <p className="text-lg text-[var(--text-secondary)] mb-6">
            Six major global banks are allegedly sitting on combined net short positions totaling <span className="text-red-400 font-bold">28.85 billion ounces</span> of silver—equivalent to <span className="text-amber-400 font-bold">36 years of global mine production</span>. At current silver prices of ~$103/oz, five of these six banks have already exceeded their Tier 1 capital in unrealized losses and are <span className="text-red-400 font-bold">technically insolvent</span>.
          </p>

          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <StatCard label="Banks Insolvent" value="5 of 6" variant="danger" />
            <StatCard label="Combined Position" value="28.85B oz" variant="warning" />
            <StatCard label="Tier 1 Wiped" value="$657B+" variant="danger" />
          </div>

          <h4 className="text-[var(--text-primary)] font-bold mb-3">The market has not yet priced this in because:</h4>
          <ol className="list-decimal list-inside space-y-2 text-[var(--text-secondary)]">
            <li>OTC derivatives are not marked-to-market daily</li>
            <li>Regulators have not yet acted publicly</li>
            <li>Banks are actively covering positions to destroy evidence before investigations begin</li>
          </ol>
        </div>
      </Section>

      {/* Key Dates */}
      <Section
        icon={<Calendar className="w-6 h-6" />}
        title="KEY DATES"
        id="key-dates"
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <DateCard date="Jan 31, 2026" bank="HSBC" event="Internal deadline" />
          <DateCard date="Feb 1, 2026" bank="Citigroup" event="DOJ deadline" urgent />
          <DateCard date="Feb 10, 2026" bank="UBS" event="Internal deadline" />
          <DateCard date="Feb 15, 2026" bank="Morgan Stanley" event="SEC deadline" />
          <DateCard date="Feb 17, 2026" bank="All Banks" event="Form SHO filings due" />
          <DateCard date="Mar 15, 2026" bank="JPMorgan" event="Unknown authority deadline" />
        </div>
      </Section>

      {/* The Positions */}
      <Section
        icon={<Building2 className="w-6 h-6" />}
        title="SECTION 1: THE POSITIONS"
        id="positions"
      >
        <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">1.1 Alleged Net Short Positions by Bank</h3>

        <div className="overflow-x-auto mb-8">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border-primary)]">
                <th className="text-left py-3 px-4 text-[var(--text-muted)]">Rank</th>
                <th className="text-left py-3 px-4 text-[var(--text-muted)]">Bank</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Net Short Position</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Entry Price (Est.)</th>
                <th className="text-left py-3 px-4 text-[var(--text-muted)]">Source</th>
              </tr>
            </thead>
            <tbody>
              <PositionRow rank={1} bank="JPMorgan Chase" position="7.95B oz" entry="$50" source="CFTC data + whistleblower" />
              <PositionRow rank={2} bank="HSBC" position="7.30B oz" entry="$50" source="Internal board leak" />
              <PositionRow rank={3} bank="UBS" position="5.20B oz" entry="$50" source="Executive directive leak" />
              <PositionRow rank={4} bank="Morgan Stanley" position="4.00B oz" entry="$72" source="SEC whistleblower (Jan 7)" />
              <PositionRow rank={5} bank="Citigroup" position="3.40B oz" entry="$50" source="DOJ investigation" />
              <PositionRow rank={6} bank="Bank of America" position="1.00B oz" entry="$50" source="OCC derivatives data" />
              <tr className="border-t-2 border-red-500/50 bg-red-500/10">
                <td className="py-3 px-4"></td>
                <td className="py-3 px-4 font-bold text-[var(--text-primary)]">TOTAL</td>
                <td className="py-3 px-4 text-right font-bold text-red-400">28.85B oz</td>
                <td colSpan={2}></td>
              </tr>
            </tbody>
          </table>
        </div>

        <h4 className="text-lg font-bold text-[var(--text-primary)] mb-4">Context for Position Sizes</h4>
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <ContextCard metric="Annual global production" value="800M oz" comparison="36x annual production" />
          <ContextCard metric="COMEX registered inventory" value="~30M oz" comparison="962x COMEX" />
          <ContextCard metric="Annual structural deficit" value="~200M oz" comparison="144x annual deficit" />
        </div>

        {/* JPMorgan Section */}
        <div className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border-primary)] mb-8">
          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">1.2 JPMorgan: The "Smart Money" Myth</h3>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-bold text-[var(--text-muted)] mb-2">THE NARRATIVE</h4>
              <p className="text-[var(--text-secondary)]">
                JPMorgan "flipped long" in 2024, accumulated 700-750M oz physical, and will profit from the squeeze.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-bold text-red-400 mb-2">THE REALITY</h4>
              <ul className="space-y-1 text-[var(--text-secondary)]">
                <li>Gross Short: <span className="text-red-400">8.7 billion oz</span></li>
                <li>Long Position: <span className="text-green-400">~750 million oz</span></li>
                <li className="font-bold text-red-400">Net Short: 7.95 billion oz</li>
              </ul>
            </div>
          </div>

          <p className="mt-4 text-[var(--text-secondary)] border-t border-[var(--border-primary)] pt-4">
            JPMorgan is not the apex predator. <span className="text-red-400 font-bold">They are the largest bagholder.</span> The "flipped long" narrative may have been deliberately planted to discourage scrutiny while they accumulated the largest short position in history.
          </p>
        </div>

        {/* Morgan Stanley Whistleblower */}
        <div className="bg-amber-500/10 rounded-xl p-6 border border-amber-500/30 mb-8">
          <h3 className="text-xl font-bold text-amber-400 mb-4">1.3 Morgan Stanley: The Whistleblower Case</h3>

          <div className="space-y-3 mb-6">
            <TimelineEvent date="Dec 24, 2025" event="Silver at $72. MS allegedly shorts heavily." />
            <TimelineEvent date="Jan 2, 2026" event="MS sends client advisory: 'Avoid physical delivery in Q1, settlement risk elevated'" />
            <TimelineEvent date="Jan 7, 2026" event="Trading desk employee files Dodd-Frank whistleblower complaint with SEC" urgent />
            <TimelineEvent date="Jan 8, 2026" event="SEC notifies MS of whistleblower receipt. 'Exit All Silver Positions' memo leaks" />
            <TimelineEvent date="Jan 9, 2026" event="MS Executive Board emergency meeting. Mandate: liquidate all positions before Feb 15" />
          </div>

          <h4 className="text-lg font-bold text-[var(--text-primary)] mb-3">Potential Criminal Charges</h4>
          <div className="grid md:grid-cols-2 gap-3">
            <ChargeCard violation="Securities Fraud" statute="15 U.S.C. § 78j(b)" penalty="20 years" />
            <ChargeCard violation="Market Manipulation" statute="7 U.S.C. § 9 (CEA)" penalty="25 years" />
            <ChargeCard violation="Commodities Fraud" statute="18 U.S.C. § 1348" penalty="25 years" />
            <ChargeCard violation="Wire Fraud" statute="18 U.S.C. § 1343" penalty="20 years" />
          </div>

          <p className="mt-4 text-red-400 font-bold text-center text-lg">
            This isn't about insolvency. It's about prison.
          </p>
        </div>
      </Section>

      {/* Insolvency Analysis */}
      <Section
        icon={<Skull className="w-6 h-6" />}
        title="SECTION 2: INSOLVENCY ANALYSIS"
        id="insolvency"
      >
        <div className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border-primary)] mb-8">
          <h4 className="text-sm font-bold text-[var(--text-muted)] mb-2">THE INSOLVENCY FORMULA</h4>
          <code className="block bg-black/50 p-4 rounded-lg text-green-400 font-mono">
            Insolvency Trigger Price = Entry Price + (Tier 1 Capital / Net Short Position)
          </code>
        </div>

        <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Bank-by-Bank Insolvency Triggers</h3>

        <div className="overflow-x-auto mb-8">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border-primary)]">
                <th className="text-left py-3 px-4 text-[var(--text-muted)]">Bank</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Net Short</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Entry</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Tier 1 Capital</th>
                <th className="text-right py-3 px-4 text-[var(--text-muted)]">Insolvency Price</th>
                <th className="text-center py-3 px-4 text-[var(--text-muted)]">Status</th>
              </tr>
            </thead>
            <tbody>
              <InsolvencyRow bank="UBS" shortPos="5.2B oz" entry="$50" tier1="$69B" insolvencyPrice="$63.27" status="insolvent" />
              <InsolvencyRow bank="HSBC" shortPos="7.3B oz" entry="$50" tier1="$180B" insolvencyPrice="$74.66" status="insolvent" />
              <InsolvencyRow bank="JPMorgan" shortPos="7.95B oz" entry="$50" tier1="$250B" insolvencyPrice="$81.45" status="insolvent" />
              <InsolvencyRow bank="Morgan Stanley" shortPos="4.0B oz" entry="$72" tier1="$80B" insolvencyPrice="$92.00" status="insolvent" />
              <InsolvencyRow bank="Citigroup" shortPos="3.4B oz" entry="$50" tier1="$150B" insolvencyPrice="$94.12" status="insolvent" />
              <InsolvencyRow bank="Bank of America" shortPos="1.0B oz" entry="$50" tier1="$190B" insolvencyPrice="$240.00" status="solvent" />
            </tbody>
          </table>
        </div>

        <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Current Losses vs Capital (@ $102.91)</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <LossCard bank="UBS" loss="$275B" tier1="$69B" wipeout="3.99x" />
          <LossCard bank="HSBC" loss="$386B" tier1="$180B" wipeout="2.14x" />
          <LossCard bank="JPMorgan" loss="$421B" tier1="$250B" wipeout="1.68x" />
          <LossCard bank="Morgan Stanley" loss="$124B" tier1="$80B" wipeout="1.55x" />
          <LossCard bank="Citigroup" loss="$180B" tier1="$150B" wipeout="1.20x" />
          <LossCard bank="Bank of America" loss="$53B" tier1="$190B" wipeout="0.28x" solvent />
        </div>
      </Section>

      {/* Cascade Timeline */}
      <Section
        icon={<Clock className="w-6 h-6" />}
        title="SECTION 5: THE CASCADE TIMELINE"
        id="cascade"
      >
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-500 via-red-500 to-red-900" />

          <div className="space-y-6 pl-12">
            <CascadeEvent
              date="Jan 23"
              day="TODAY"
              event="Silver $102.91. All banks except BAC technically insolvent."
              price="$103"
              current
            />
            <CascadeEvent
              date="Jan 24-25"
              day="Day 1-2"
              event="UBS liquidity stress becomes acute. Emergency board meetings. Swiss regulator consultation."
              price="$113-123"
            />
            <CascadeEvent
              date="Jan 26-27"
              day="Day 3-4"
              event="HSBC margin call failure likely. UK Treasury alerted."
              price="$133-143"
            />
            <CascadeEvent
              date="Jan 28"
              day="Day 5"
              event="Morgan Stanley margin call failure likely. NYSE trading halts possible."
              price="$153"
            />
            <CascadeEvent
              date="Jan 31"
              day="Day 8"
              event="HSBC internal deadline. First official failure?"
              price="$183"
              critical
            />
            <CascadeEvent
              date="Feb 1"
              day="Day 9"
              event="Citigroup DOJ deadline. Criminal charges filed?"
              price="$193"
              critical
            />
            <CascadeEvent
              date="Feb 2-4"
              day="Day 10-12"
              event="JPMorgan liquidity crisis. Too big to fail invoked."
              price="$210-230"
            />
            <CascadeEvent
              date="Feb 17"
              day="Day 25"
              event="First Form SHO filings due. All short positions disclosed."
              price="$350"
            />
            <CascadeEvent
              date="Mar 15"
              day="Day 51"
              event="JPMorgan deadline. Mega-merger or nationalization."
              price="$600-800"
              critical
            />
            <CascadeEvent
              date="Mar 20"
              day="Day 56"
              event="COMEX potential default. Price discovery breaks."
              price="$1,000+?"
              critical
            />
          </div>
        </div>
      </Section>

      {/* Price Projections */}
      <Section
        icon={<Target className="w-6 h-6" />}
        title="SECTION 6: PRICE PROJECTIONS"
        id="projections"
      >
        <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Silver Price Targets by Covering Scenario</h3>

        <div className="space-y-4 mb-8">
          <PriceScenario scenario="MS alone" banks="Morgan Stanley" position="4.0B oz" target="$289" />
          <PriceScenario scenario="MS + Citi" banks="+ Citigroup" position="7.4B oz" target="$400-500" />
          <PriceScenario scenario="+ HSBC" banks="+ HSBC" position="14.7B oz" target="$700-900" />
          <PriceScenario scenario="All except JPM" banks="+ UBS" position="19.9B oz" target="$1,200-1,500" />
          <PriceScenario scenario="All banks" banks="+ JPMorgan" position="28.85B oz" target="$2,000-3,000+" critical />
          <PriceScenario scenario="COMEX default" banks="Force majeure" position="N/A" target="Price breaks" critical />
        </div>

        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
          <h4 className="text-lg font-bold text-red-400 mb-4">Loss Calculations at $1,000 Silver</h4>
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-3xl font-black text-red-400">$27.3T</div>
              <div className="text-sm text-[var(--text-muted)]">Total Losses</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-amber-400">$28T</div>
              <div className="text-sm text-[var(--text-muted)]">US Annual GDP</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-[var(--text-primary)]">$105T</div>
              <div className="text-sm text-[var(--text-muted)]">Global Annual GDP</div>
            </div>
          </div>
          <p className="text-sm text-[var(--text-secondary)] text-center">
            For context: 2008 Financial Crisis total losses were ~$2 trillion
          </p>
        </div>
      </Section>

      {/* What to Watch */}
      <Section
        icon={<BarChart3 className="w-6 h-6" />}
        title="SECTION 12: WHAT TO WATCH"
        id="watch"
      >
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border-primary)]">
            <h4 className="font-bold text-[var(--text-primary)] mb-4">Daily Monitoring Checklist</h4>
            <ul className="space-y-2 text-[var(--text-secondary)]">
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Silver spot price (targets: $110, $120, $150, $200, $289)
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Bank stock prices vs SPY (looking for divergence)
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                PSLV premium/discount to NAV
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Fed repo facility usage
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                COMEX delivery notices
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Physical dealer inventory/premiums
              </li>
              <li className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Shanghai vs COMEX spread
              </li>
            </ul>
          </div>

          <div className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border-primary)]">
            <h4 className="font-bold text-[var(--text-primary)] mb-4">News Triggers</h4>
            <ul className="space-y-2 text-[var(--text-secondary)]">
              <li>Any SEC/DOJ/CFTC statements regarding precious metals</li>
              <li>Any Fed emergency meeting announcements</li>
              <li>Any bank executive departures</li>
              <li>Any FDIC activity over weekends</li>
              <li>Any "anonymous source" stories about bank stress</li>
              <li>Any trading halts in bank stocks</li>
            </ul>
          </div>
        </div>
      </Section>

      {/* Scenario Analysis */}
      <Section
        icon={<Scale className="w-6 h-6" />}
        title="SECTION 13: SCENARIO ANALYSIS"
        id="scenarios"
      >
        <div className="grid md:grid-cols-3 gap-6">
          <ScenarioCard
            title="Bull Case (For Silver)"
            probability={60}
            variant="danger"
            points={[
              "Banks forced to cover, price discovery continues",
              "Silver reaches $500-1,000+",
              "Multiple bank failures",
              "Fed forced to intervene",
              "Physical silver becomes unavailable"
            ]}
          />
          <ScenarioCard
            title="Base Case"
            probability={30}
            variant="warning"
            points={[
              "Partial covering, partial rule changes",
              "Silver reaches $200-400",
              "1-2 bank failures, others receive support",
              "COMEX implements cash settlement",
              "Two-tier market emerges"
            ]}
          />
          <ScenarioCard
            title="Bear Case (For Silver)"
            probability={10}
            variant="success"
            points={[
              "Coordinated intervention suppresses price",
              "COMEX declares force majeure",
              "Paper price crashed via rule changes",
              "Physical market decouples",
              "Banks survive but silver market destroyed"
            ]}
          />
        </div>
      </Section>

      {/* Footer Quote */}
      <section className="max-w-4xl mx-auto px-4 py-16 text-center">
        <blockquote className="text-xl italic text-[var(--text-secondary)] mb-4">
          "The market can remain irrational longer than you can remain solvent."
        </blockquote>
        <p className="text-[var(--text-muted)]">— John Maynard Keynes</p>

        <blockquote className="text-xl italic text-amber-400 mt-8 mb-4">
          "But the market cannot remain irrational longer than the silver can remain undelivered."
        </blockquote>
        <p className="text-[var(--text-muted)]">— Fault.Watch, January 2026</p>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border-primary)] py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-[var(--text-muted)] text-sm mb-4">
            Report Version 1.0 | Last Updated: January 23, 2026
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Live Dashboard
          </Link>
        </div>
      </footer>
    </div>
  )
}

// Helper Components

function Section({ icon, title, id, children }: {
  icon: React.ReactNode
  title: string
  id: string
  children: React.ReactNode
}) {
  return (
    <section id={id} className="max-w-4xl mx-auto px-4 mb-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-red-500/20 rounded-lg text-red-400">
            {icon}
          </div>
          <h2 className="text-2xl font-bold text-[var(--text-primary)]">{title}</h2>
        </div>
        {children}
      </motion.div>
    </section>
  )
}

function StatCard({ label, value, variant }: { label: string; value: string; variant: 'danger' | 'warning' | 'success' }) {
  const colors = {
    danger: 'bg-red-500/20 border-red-500/30 text-red-400',
    warning: 'bg-amber-500/20 border-amber-500/30 text-amber-400',
    success: 'bg-green-500/20 border-green-500/30 text-green-400'
  }
  return (
    <div className={`${colors[variant]} border rounded-xl p-4 text-center`}>
      <div className="text-2xl font-black">{value}</div>
      <div className="text-sm text-[var(--text-muted)]">{label}</div>
    </div>
  )
}

function DateCard({ date, bank, event, urgent }: { date: string; bank: string; event: string; urgent?: boolean }) {
  return (
    <div className={`p-4 rounded-xl border ${urgent ? 'bg-red-500/20 border-red-500/30' : 'bg-[var(--bg-secondary)] border-[var(--border-primary)]'}`}>
      <div className="text-xs text-[var(--text-muted)]">{date}</div>
      <div className={`font-bold ${urgent ? 'text-red-400' : 'text-[var(--text-primary)]'}`}>{bank}</div>
      <div className="text-sm text-[var(--text-secondary)]">{event}</div>
    </div>
  )
}

function PositionRow({ rank, bank, position, entry, source }: {
  rank: number; bank: string; position: string; entry: string; source: string
}) {
  return (
    <tr className="border-b border-[var(--border-primary)]">
      <td className="py-3 px-4 text-[var(--text-muted)]">{rank}</td>
      <td className="py-3 px-4 font-bold text-[var(--text-primary)]">{bank}</td>
      <td className="py-3 px-4 text-right text-red-400 font-mono">{position}</td>
      <td className="py-3 px-4 text-right text-[var(--text-secondary)]">{entry}</td>
      <td className="py-3 px-4 text-[var(--text-muted)] text-sm">{source}</td>
    </tr>
  )
}

function ContextCard({ metric, value, comparison }: { metric: string; value: string; comparison: string }) {
  return (
    <div className="bg-[var(--bg-secondary)] rounded-xl p-4 border border-[var(--border-primary)]">
      <div className="text-sm text-[var(--text-muted)]">{metric}</div>
      <div className="text-xl font-bold text-[var(--text-primary)]">{value}</div>
      <div className="text-amber-400 font-bold">{comparison}</div>
    </div>
  )
}

function TimelineEvent({ date, event, urgent }: { date: string; event: string; urgent?: boolean }) {
  return (
    <div className={`flex gap-4 p-3 rounded-lg ${urgent ? 'bg-red-500/20' : 'bg-black/20'}`}>
      <div className={`text-sm font-bold ${urgent ? 'text-red-400' : 'text-amber-400'} whitespace-nowrap`}>{date}</div>
      <div className="text-[var(--text-secondary)]">{event}</div>
    </div>
  )
}

function ChargeCard({ violation, statute, penalty }: { violation: string; statute: string; penalty: string }) {
  return (
    <div className="bg-black/30 rounded-lg p-3">
      <div className="font-bold text-[var(--text-primary)]">{violation}</div>
      <div className="text-xs text-[var(--text-muted)]">{statute}</div>
      <div className="text-red-400 font-bold">{penalty}</div>
    </div>
  )
}

function InsolvencyRow({ bank, shortPos, entry, tier1, insolvencyPrice, status }: {
  bank: string; shortPos: string; entry: string; tier1: string; insolvencyPrice: string; status: 'insolvent' | 'solvent'
}) {
  return (
    <tr className="border-b border-[var(--border-primary)]">
      <td className="py-3 px-4 font-bold text-[var(--text-primary)]">{bank}</td>
      <td className="py-3 px-4 text-right text-[var(--text-secondary)]">{shortPos}</td>
      <td className="py-3 px-4 text-right text-[var(--text-secondary)]">{entry}</td>
      <td className="py-3 px-4 text-right text-[var(--text-secondary)]">{tier1}</td>
      <td className="py-3 px-4 text-right font-bold text-amber-400">{insolvencyPrice}</td>
      <td className="py-3 px-4 text-center">
        {status === 'insolvent' ? (
          <span className="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">INSOLVENT</span>
        ) : (
          <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">SOLVENT</span>
        )}
      </td>
    </tr>
  )
}

function LossCard({ bank, loss, tier1, wipeout, solvent }: {
  bank: string; loss: string; tier1: string; wipeout: string; solvent?: boolean
}) {
  return (
    <div className={`p-4 rounded-xl border ${solvent ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
      <div className="font-bold text-[var(--text-primary)]">{bank}</div>
      <div className="flex justify-between mt-2">
        <span className="text-[var(--text-muted)]">Loss</span>
        <span className={solvent ? 'text-green-400' : 'text-red-400'}>{loss}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-[var(--text-muted)]">Tier 1</span>
        <span className="text-[var(--text-secondary)]">{tier1}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-[var(--text-muted)]">Wipeout</span>
        <span className={`font-bold ${solvent ? 'text-green-400' : 'text-red-400'}`}>{wipeout}</span>
      </div>
    </div>
  )
}

function CascadeEvent({ date, day, event, price, current, critical }: {
  date: string; day: string; event: string; price: string; current?: boolean; critical?: boolean
}) {
  return (
    <div className={`relative pl-6 ${current ? 'opacity-100' : 'opacity-80'}`}>
      <div className={`absolute -left-6 top-2 w-4 h-4 rounded-full border-2 ${
        current ? 'bg-amber-500 border-amber-300 shadow-lg shadow-amber-500/50' :
        critical ? 'bg-red-500 border-red-300' :
        'bg-gray-600 border-gray-500'
      }`} />
      <div className={`p-4 rounded-xl ${
        current ? 'bg-amber-500/20 border border-amber-500/30' :
        critical ? 'bg-red-500/10 border border-red-500/30' :
        'bg-[var(--bg-secondary)] border border-[var(--border-primary)]'
      }`}>
        <div className="flex justify-between items-center mb-2">
          <span className={`font-bold ${current ? 'text-amber-400' : critical ? 'text-red-400' : 'text-[var(--text-primary)]'}`}>
            {date}
          </span>
          <span className="text-xs text-[var(--text-muted)]">{day}</span>
        </div>
        <p className="text-[var(--text-secondary)]">{event}</p>
        <div className="mt-2 text-sm text-[var(--text-muted)]">Silver est: {price}</div>
      </div>
    </div>
  )
}

function PriceScenario({ scenario, banks, position, target, critical }: {
  scenario: string; banks: string; position: string; target: string; critical?: boolean
}) {
  return (
    <div className={`flex items-center justify-between p-4 rounded-xl border ${
      critical ? 'bg-red-500/20 border-red-500/30' : 'bg-[var(--bg-secondary)] border-[var(--border-primary)]'
    }`}>
      <div>
        <div className={`font-bold ${critical ? 'text-red-400' : 'text-[var(--text-primary)]'}`}>{scenario}</div>
        <div className="text-sm text-[var(--text-muted)]">{banks}</div>
      </div>
      <div className="text-right">
        <div className="text-sm text-[var(--text-muted)]">{position}</div>
        <div className={`text-xl font-black ${critical ? 'text-red-400' : 'text-amber-400'}`}>{target}</div>
      </div>
    </div>
  )
}

function ScenarioCard({ title, probability, variant, points }: {
  title: string
  probability: number
  variant: 'danger' | 'warning' | 'success'
  points: string[]
}) {
  const colors = {
    danger: 'border-red-500/30 bg-red-500/10',
    warning: 'border-amber-500/30 bg-amber-500/10',
    success: 'border-green-500/30 bg-green-500/10'
  }
  const textColors = {
    danger: 'text-red-400',
    warning: 'text-amber-400',
    success: 'text-green-400'
  }

  return (
    <div className={`rounded-xl border p-6 ${colors[variant]}`}>
      <h4 className={`font-bold mb-2 ${textColors[variant]}`}>{title}</h4>
      <div className="text-3xl font-black text-[var(--text-primary)] mb-4">{probability}%</div>
      <ul className="space-y-2">
        {points.map((point, i) => (
          <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
            <span className={`${textColors[variant]}`}>•</span>
            {point}
          </li>
        ))}
      </ul>
    </div>
  )
}
