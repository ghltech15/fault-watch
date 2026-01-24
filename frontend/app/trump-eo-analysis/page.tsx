'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  ArrowLeft,
  AlertTriangle,
  FileText,
  Scale,
  Building2,
  Coins,
  Globe,
  Clock,
  Target,
  TrendingUp,
  Shield,
  Flag,
  Landmark,
  CheckCircle2,
  XCircle,
  HelpCircle
} from 'lucide-react'

const MONETARY_RESTRUCTURING = [
  { eo: 'Strategic Bitcoin Reserve', date: 'Mar 6, 2025', relevance: 'Creates alternative reserve asset structure' },
  { eo: 'Sovereign Wealth Fund', date: 'Feb 3, 2025', relevance: 'Monetize asset side of balance sheet - Bessent' },
  { eo: 'Fort Knox Audit', date: 'Feb 20, 2025', relevance: 'Sets stage for gold revaluation' },
  { eo: 'Gold Tariff Exemption', date: 'Sep 5, 2025', relevance: '0% tariff on gold imports - facilitating inflows' },
  { eo: 'Gold Tariff (39%)', date: 'Aug 8, 2025', relevance: '39% on 100oz+ bars - preventing arbitrage before revaluation' },
  { eo: 'GENIUS Act (Stablecoin Law)', date: 'Jul 18, 2025', relevance: '100% reserve backing with Treasuries - creates USD demand' },
]

const BANK_REGULATORY = [
  { eo: 'Regulatory Freeze', date: 'Jan 20, 2025', relevance: 'Halts Basel III Endgame (capital requirements)' },
  { eo: 'Independent Agency Control', date: 'Feb 18, 2025', relevance: 'Brings FDIC, SEC under White House control' },
  { eo: 'Fair Banking EO', date: 'Aug 7, 2025', relevance: 'Removes reputation risk from examinations' },
  { eo: 'Basel III Halted', date: 'Throughout 2025', relevance: 'Banks NOT required to increase capital' },
  { eo: 'Bank Deregulation', date: 'Throughout 2025', relevance: '10-to-1 deregulation agenda' },
]

const PRECIOUS_METALS = [
  { eo: 'Critical Minerals EO', date: 'Mar 20, 2025', relevance: 'Emergency powers for domestic mineral production' },
  { eo: 'Gold added to critical list', date: 'Mar 20, 2025', relevance: 'Now includes gold, copper, uranium, potash' },
  { eo: 'EO 14330 (401k Access)', date: 'Aug 7, 2025', relevance: 'Opens 7T+ retirement funds to commodities/silver' },
  { eo: 'Gold Tariff Exemptions', date: 'Sep 5, 2025', relevance: 'Facilitates gold inflows' },
  { eo: 'Defense Production Act', date: 'Various', relevance: 'Invoked for mineral supply chains' },
]

const CHINA_TRADE = [
  { eo: 'China Tariffs', date: 'Feb-Nov 2025', relevance: 'Up to 145% at peak, settled at 30%' },
  { eo: 'Rare Earth Controls', date: 'Various', relevance: 'China responds with export controls' },
  { eo: 'China Silver Export Ban', date: 'Jan 1, 2026', relevance: '65% of global supply restricted' },
  { eo: 'Critical Minerals Deal', date: 'Nov 2025', relevance: 'China suspends export controls on rare earths' },
]

export default function TrumpEOAnalysisPage() {
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
          <div className="flex items-center gap-4">
            <Link href="/crisis-dashboard" className="text-sm text-gray-400 hover:text-white">Crisis Dashboard</Link>
            <Link href="/deep-dive" className="text-sm text-gray-400 hover:text-white">Deep Dive</Link>
          </div>
        </div>
      </header>

      {/* Unverified Notice */}
      <section className="max-w-5xl mx-auto px-4 pt-8 pb-4">
        <div className="bg-amber-500/20 border-2 border-amber-500 rounded-xl p-4">
          <div className="flex items-center justify-center gap-3 text-amber-400 mb-2">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-bold">UNVERIFIED SPECULATIVE ANALYSIS</span>
            <AlertTriangle className="w-5 h-5" />
          </div>
          <p className="text-center text-amber-200/80 text-sm">
            This analysis explores potential connections between executive orders and financial events.
            These are theories and hypotheses only - NOT verified facts or predictions.
          </p>
        </div>
      </section>

      {/* Hero */}
      <section className="relative py-12 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-transparent" />
        <div className="max-w-4xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-blue-500/20 text-blue-400 px-4 py-2 rounded-full mb-6">
              <Flag className="w-4 h-4" />
              <span className="text-sm font-bold">EXECUTIVE ORDER ANALYSIS</span>
            </div>
            <h1 className="text-3xl md:text-5xl font-black text-[var(--text-primary)] mb-4">
              THE BIGGER PICTURE
            </h1>
            <p className="text-xl text-blue-400 font-bold mb-4">
              Trump Executive Orders & The Silver/Bank Crisis Matrix
            </p>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">
              230+ executive orders analyzed against Fault.Watch banking crisis scenarios reveal a potential pattern of positioning for major monetary/financial system restructuring.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Legal Notice */}
      <section className="max-w-5xl mx-auto px-4 mb-8">
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Scale className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <span className="font-bold text-red-400">LEGAL NOTICE:</span>
              <span className="text-[var(--text-secondary)]"> This is speculative analysis exploring possible connections. Nothing here constitutes financial, investment, or legal advice. These are hypotheses, not predictions. Always conduct your own research.</span>
            </div>
          </div>
        </div>
      </section>

      {/* Executive Summary */}
      <Section icon={<FileText className="w-6 h-6" />} title="EXECUTIVE SUMMARY" id="summary">
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mb-6">
          <p className="text-lg text-[var(--text-secondary)]">
            After analyzing 230+ Trump executive orders from 2025-2026 against the Fault.Watch banking crisis scenarios,
            a coherent pattern emerges. These orders, when viewed collectively, appear to be positioning the United States
            for a <span className="text-blue-400 font-bold">major monetary/financial system restructuring</span> that
            converges with the alleged silver short squeeze timeline.
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          <PatternCard
            icon={<Landmark className="w-5 h-5" />}
            title="Alternative Reserves"
            description="Bitcoin reserve, SWF, gold positioning"
            color="blue"
          />
          <PatternCard
            icon={<Building2 className="w-5 h-5" />}
            title="Bank Deregulation"
            description="Basel III halted, oversight reduced"
            color="amber"
          />
          <PatternCard
            icon={<Coins className="w-5 h-5" />}
            title="Commodity Channels"
            description="401k access to silver/gold opened"
            color="green"
          />
          <PatternCard
            icon={<Globe className="w-5 h-5" />}
            title="Supply Constraints"
            description="China silver export restrictions"
            color="red"
          />
        </div>
      </Section>

      {/* Monetary System Restructuring */}
      <Section icon={<Landmark className="w-6 h-6" />} title="1. MONETARY SYSTEM RESTRUCTURING" id="monetary">
        <EOTable data={MONETARY_RESTRUCTURING} />
        <PatternBox pattern="Building alternative reserve infrastructure BEFORE potential dollar crisis." color="blue" />
      </Section>

      {/* Bank Regulatory Overhaul */}
      <Section icon={<Building2 className="w-6 h-6" />} title="2. BANK REGULATORY OVERHAUL" id="banks">
        <EOTable data={BANK_REGULATORY} />
        <PatternBox pattern="REDUCING capital requirements and oversight at precisely the moment banks face potential insolvency from silver shorts." color="amber" />
      </Section>

      {/* Precious Metals */}
      <Section icon={<Coins className="w-6 h-6" />} title="3. PRECIOUS METALS & COMMODITIES" id="metals">
        <EOTable data={PRECIOUS_METALS} />
        <PatternBox pattern="Creating infrastructure for commodity-backed monetary system while opening massive new demand channels." color="green" />
      </Section>

      {/* China Trade */}
      <Section icon={<Globe className="w-6 h-6" />} title="4. CHINA TRADE WAR & SILVER SUPPLY" id="china">
        <EOTable data={CHINA_TRADE} />
        <PatternBox pattern="Trade war pressure caused China to restrict silver exports - tightening supply at critical moment." color="red" />
      </Section>

      {/* Convergence Timeline */}
      <Section icon={<Clock className="w-6 h-6" />} title="THE CONVERGENCE TIMELINE" id="timeline">
        <div className="space-y-6">
          <TimelinePhase
            phase="PHASE 1"
            title="FOUNDATION LAYING"
            period="Jan-Aug 2025"
            events={[
              'Jan 20: Regulatory freeze, Basel III halted',
              'Jan 23: Digital asset EO, crypto-friendly',
              'Feb 3: Sovereign Wealth Fund ordered',
              'Feb 20: Fort Knox audit announced',
              'Mar 6: Strategic Bitcoin Reserve created',
              'Mar 20: Critical Minerals emergency powers',
              'Aug 7: EO 14330 - 401k access to commodities',
              'Aug 7: Fair Banking EO - reduces bank oversight',
            ]}
            color="blue"
          />
          <TimelinePhase
            phase="PHASE 2"
            title="PRECIOUS METALS POSITIONING"
            period="Aug-Nov 2025"
            events={[
              'Aug 8: 39% gold tariff (100oz+ bars)',
              'Sep 5: Gold tariff exemption for aligned partners',
              'Jul 18: GENIUS Act signed (stablecoins)',
              'Nov: China trade deal, rare earth controls lifted',
            ]}
            color="amber"
          />
          <TimelinePhase
            phase="PHASE 3"
            title="CRISIS WINDOW"
            period="Dec 2025-Feb 2026"
            events={[
              'Dec 26-31: $125.6B Fed repo injections',
              'Dec 26-29: CME margin hikes 47%',
              'Jan 1, 2026: China silver export ban effective',
              'Jan 23, 2026: Silver $103+ (5 banks insolvent)',
              'Jan 31: HSBC alleged deadline',
              'Feb 1: Citi DOJ alleged deadline',
              '~Feb: EO 14330 DOL guidance due (180 days)',
              'Feb 15: MS SEC investigation alleged',
            ]}
            color="red"
            current
          />
          <TimelinePhase
            phase="PHASE 4"
            title="POTENTIAL RESTRUCTURING"
            period="Feb-Mar 2026"
            events={[
              'Gold revaluation? (Bitcoin Act Section 9)',
              'SWF capitalization?',
              'Bank bailouts/failures?',
              'New monetary framework?',
            ]}
            color="purple"
            future
          />
        </div>
      </Section>

      {/* Hypotheses */}
      <Section icon={<HelpCircle className="w-6 h-6" />} title="THE THEORY: WHAT THE PUZZLE REVEALS" id="theory">
        <div className="grid md:grid-cols-3 gap-6">
          <HypothesisCard
            number={1}
            title="Controlled Demolition"
            description="The administration may be aware of the banking system's silver exposure and is preparing alternative infrastructure."
            points={[
              'Reducing capital requirements (Basel III halt)',
              'Building alternative infrastructure (Bitcoin reserve, SWF)',
              'Opening commodity demand channels (EO 14330)',
              'Positioning for gold revaluation (Fort Knox audit)',
            ]}
            outcome="When banks fail, the government has alternative reserve assets and a restructuring mechanism ready."
          />
          <HypothesisCard
            number={2}
            title="Asset Monetization Strategy"
            description="Secretary Bessent: We're going to monetize the asset side of the U.S. balance sheet"
            points={[
              'Gold revaluation: $42.22 → $3,000+ = ~$750B',
              'Bitcoin reserve: Seized crypto becomes strategic asset',
              'Federal lands: Potential SWF funding source',
              'Stablecoins: GENIUS Act creates Treasury demand',
            ]}
            outcome="Create fiscal headroom for bank bailouts without Congressional appropriations."
          />
          <HypothesisCard
            number={3}
            title="Great Reset Preparation"
            description="Combination of policies positioning for fundamental system change."
            points={[
              'Dollar system restructuring',
              'Partial gold backing return',
              'Digital currency integration',
              'Bank consolidation/nationalization',
            ]}
            outcome="Complete monetary system overhaul with new reserve asset structure."
          />
        </div>
      </Section>

      {/* What's Missing */}
      <Section icon={<XCircle className="w-6 h-6" />} title="WHAT'S MISSING (UNCONFIRMED)" id="missing">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MissingItem text="No explicit EO on bank bailout mechanisms" />
          <MissingItem text="No explicit gold revaluation order (yet)" />
          <MissingItem text="Fort Knox audit results not released" />
          <MissingItem text="Exact bank silver positions unconfirmed" />
          <MissingItem text="DOL guidance on EO 14330 not yet issued" />
        </div>
      </Section>

      {/* Conclusion */}
      <Section icon={<Target className="w-6 h-6" />} title="CONCLUSION: THE BIGGER PICTURE" id="conclusion">
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-xl p-6 mb-6">
          <p className="text-[var(--text-secondary)] mb-4">
            The executive order pattern suggests preparation for a <span className="text-blue-400 font-bold">major financial system event</span>:
          </p>
          <div className="grid md:grid-cols-2 gap-3">
            <ConclusionPoint icon={<CheckCircle2 />} text="Alternative reserve assets being positioned (gold, Bitcoin, SWF)" />
            <ConclusionPoint icon={<CheckCircle2 />} text="Bank oversight reduced at moment of maximum vulnerability" />
            <ConclusionPoint icon={<CheckCircle2 />} text="Commodity access channels being opened (EO 14330)" />
            <ConclusionPoint icon={<CheckCircle2 />} text="Gold infrastructure being prepared (tariffs, audit, revaluation)" />
            <ConclusionPoint icon={<CheckCircle2 />} text="Fed backstop expanded (unlimited repo)" />
            <ConclusionPoint icon={<CheckCircle2 />} text="China supply constraints tightening precious metals" />
          </div>
        </div>

        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6">
          <h4 className="font-bold text-amber-400 mb-3">Whether this is...</h4>
          <ul className="space-y-2 text-[var(--text-secondary)]">
            <li><span className="text-amber-400 font-bold">Intentional restructuring</span> (controlled demolition theory)</li>
            <li><span className="text-amber-400 font-bold">Crisis preparation</span> (they know what's coming)</li>
            <li><span className="text-amber-400 font-bold">Coincidental alignment</span> (separate policy goals converging)</li>
          </ul>
          <p className="mt-4 text-[var(--text-secondary)]">
            ...remains to be seen. But the convergence of these policies with the alleged bank insolvency timeline is remarkable.
          </p>
        </div>
      </Section>

      {/* Monitoring Priorities */}
      <Section icon={<Shield className="w-6 h-6" />} title="MONITORING PRIORITIES" id="monitoring">
        <div className="grid md:grid-cols-2 gap-6">
          <MonitoringList
            title="Immediate (Jan 25 - Feb 15, 2026)"
            items={[
              'DOL guidance on EO 14330',
              'Fort Knox audit results',
              'Fed repo facility usage',
              'Bank stock performance',
              'Silver price vs alleged trigger levels',
            ]}
            urgent
          />
          <MonitoringList
            title="Medium-term (Feb - Mar 2026)"
            items={[
              'Gold revaluation legislation progress',
              'SWF funding announcement',
              'Bank failure announcements',
              'FDIC actions',
              'Form SHO disclosures (Feb 17)',
            ]}
          />
        </div>

        <div className="mt-6 bg-red-500/10 border border-red-500/30 rounded-xl p-6">
          <h4 className="font-bold text-red-400 mb-3">Key Signals to Watch</h4>
          <div className="grid md:grid-cols-2 gap-2 text-sm text-[var(--text-secondary)]">
            <div>Any EO invoking emergency banking powers</div>
            <div>Treasury announcements on "asset monetization"</div>
            <div>Fed emergency lending facility expansion</div>
            <div>Gold revaluation legislative action</div>
            <div>Bank merger/acquisition announcements</div>
          </div>
        </div>
      </Section>

      {/* Footer */}
      <footer className="border-t border-[var(--border-primary)] py-8 mt-12">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-[var(--text-muted)] text-sm mb-4">
            Analysis Date: January 24, 2026 | Status: Hypothesis Development - Not Financial Advice
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/" className="text-blue-400 hover:text-blue-300 transition-colors">
              Main Dashboard
            </Link>
            <Link href="/crisis-dashboard" className="text-blue-400 hover:text-blue-300 transition-colors">
              Crisis Dashboard
            </Link>
            <Link href="/deep-dive" className="text-blue-400 hover:text-blue-300 transition-colors">
              Deep Dive Report
            </Link>
          </div>
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
    <section id={id} className="max-w-5xl mx-auto px-4 mb-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
            {icon}
          </div>
          <h2 className="text-xl font-bold text-[var(--text-primary)]">{title}</h2>
        </div>
        {children}
      </motion.div>
    </section>
  )
}

function PatternCard({ icon, title, description, color }: {
  icon: React.ReactNode
  title: string
  description: string
  color: 'blue' | 'amber' | 'green' | 'red'
}) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    amber: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
  }

  return (
    <div className={`${colors[color]} border rounded-xl p-4`}>
      <div className="mb-2">{icon}</div>
      <h4 className="font-bold mb-1">{title}</h4>
      <p className="text-sm text-[var(--text-muted)]">{description}</p>
    </div>
  )
}

function EOTable({ data }: { data: { eo: string; date: string; relevance: string }[] }) {
  return (
    <div className="overflow-x-auto mb-4">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--border-primary)]">
            <th className="text-left py-3 px-4 text-[var(--text-muted)] font-normal">EO / Action</th>
            <th className="text-left py-3 px-4 text-[var(--text-muted)] font-normal">Date</th>
            <th className="text-left py-3 px-4 text-[var(--text-muted)] font-normal">Relevance to Crisis</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-b border-[var(--border-primary)]/50">
              <td className="py-3 px-4 font-bold text-[var(--text-primary)]">{row.eo}</td>
              <td className="py-3 px-4 text-[var(--text-secondary)]">{row.date}</td>
              <td className="py-3 px-4 text-[var(--text-secondary)]">{row.relevance}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function PatternBox({ pattern, color }: { pattern: string; color: 'blue' | 'amber' | 'green' | 'red' }) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    amber: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
  }

  return (
    <div className={`${colors[color]} border rounded-lg p-4`}>
      <span className="font-bold">PATTERN: </span>
      <span className="text-[var(--text-secondary)]">{pattern}</span>
    </div>
  )
}

function TimelinePhase({ phase, title, period, events, color, current, future }: {
  phase: string
  title: string
  period: string
  events: string[]
  color: 'blue' | 'amber' | 'red' | 'purple'
  current?: boolean
  future?: boolean
}) {
  const colors = {
    blue: 'border-blue-500/50 bg-blue-500/5',
    amber: 'border-amber-500/50 bg-amber-500/5',
    red: 'border-red-500/50 bg-red-500/5',
    purple: 'border-purple-500/50 bg-purple-500/5',
  }
  const textColors = {
    blue: 'text-blue-400',
    amber: 'text-amber-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  }

  return (
    <div className={`border-l-4 ${colors[color]} rounded-r-xl p-4 ${current ? 'ring-2 ring-red-500/50' : ''}`}>
      <div className="flex items-center gap-3 mb-3">
        <span className={`font-bold ${textColors[color]}`}>{phase}</span>
        <span className="text-[var(--text-primary)] font-bold">{title}</span>
        <span className="text-[var(--text-muted)] text-sm">({period})</span>
        {current && <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded font-bold animate-pulse">NOW</span>}
        {future && <span className="bg-purple-500/50 text-purple-200 text-xs px-2 py-0.5 rounded">UPCOMING</span>}
      </div>
      <ul className="space-y-1 text-sm text-[var(--text-secondary)]">
        {events.map((event, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className={`${textColors[color]}`}>├─</span>
            {event}
          </li>
        ))}
      </ul>
    </div>
  )
}

function HypothesisCard({ number, title, description, points, outcome }: {
  number: number
  title: string
  description: string
  points: string[]
  outcome: string
}) {
  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <span className="bg-blue-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold">{number}</span>
        <h4 className="font-bold text-[var(--text-primary)]">{title}</h4>
      </div>
      <p className="text-sm text-[var(--text-secondary)] mb-3">{description}</p>
      <ul className="space-y-1 text-sm text-[var(--text-muted)] mb-4">
        {points.map((point, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-blue-400">•</span>
            {point}
          </li>
        ))}
      </ul>
      <div className="border-t border-[var(--border-primary)] pt-3">
        <span className="text-xs text-blue-400 font-bold">OUTCOME: </span>
        <span className="text-xs text-[var(--text-secondary)]">{outcome}</span>
      </div>
    </div>
  )
}

function MissingItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2 bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
      <XCircle className="w-4 h-4 text-gray-400 flex-shrink-0" />
      <span className="text-sm text-[var(--text-secondary)]">{text}</span>
    </div>
  )
}

function ConclusionPoint({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex items-start gap-2">
      <span className="text-green-400 flex-shrink-0">{icon}</span>
      <span className="text-sm text-[var(--text-secondary)]">{text}</span>
    </div>
  )
}

function MonitoringList({ title, items, urgent }: { title: string; items: string[]; urgent?: boolean }) {
  return (
    <div className={`rounded-xl p-5 border ${urgent ? 'bg-red-500/10 border-red-500/30' : 'bg-[var(--bg-secondary)] border-[var(--border-primary)]'}`}>
      <h4 className={`font-bold mb-3 ${urgent ? 'text-red-400' : 'text-[var(--text-primary)]'}`}>{title}</h4>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
            <input type="checkbox" className="rounded" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
