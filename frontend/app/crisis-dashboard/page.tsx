'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  ArrowLeft,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Clock,
  DollarSign,
  Skull,
  Building2,
  Target,
  BarChart3,
  Calendar,
  Zap
} from 'lucide-react'

// Bank data
const BANK_DATA = [
  { name: 'UBS', shortPos: '5.2B oz', entry: '$50', tier1: '$69B', triggerPrice: 63.27, loss: '$275B', wipeout: '3.99x', daysToExhaust: '1-2', exhaustPercent: 95 },
  { name: 'HSBC', shortPos: '7.3B oz', entry: '$50', tier1: '$180B', triggerPrice: 74.66, loss: '$386B', wipeout: '2.14x', daysToExhaust: '3-4', exhaustPercent: 85 },
  { name: 'JPMorgan', shortPos: '7.95B oz', entry: '$50', tier1: '$250B', triggerPrice: 81.45, loss: '$421B', wipeout: '1.68x', daysToExhaust: '10-12', exhaustPercent: 60 },
  { name: 'Morgan Stanley', shortPos: '4.0B oz', entry: '$72', tier1: '$80B', triggerPrice: 92.00, loss: '$124B', wipeout: '1.55x', daysToExhaust: '4-5', exhaustPercent: 75 },
  { name: 'Citigroup', shortPos: '3.4B oz', entry: '$50', tier1: '$150B', triggerPrice: 94.12, loss: '$180B', wipeout: '1.20x', daysToExhaust: '15-18', exhaustPercent: 45 },
  { name: 'Bank of America', shortPos: '1.0B oz', entry: '$50', tier1: '$190B', triggerPrice: 240.00, loss: '$53B', wipeout: '0.28x', daysToExhaust: '50-60', exhaustPercent: 15, solvent: true },
]

const DEADLINES = [
  { bank: 'HSBC', date: new Date('2026-01-31'), label: 'Internal Deadline' },
  { bank: 'Citigroup', date: new Date('2026-02-01'), label: 'DOJ Deadline' },
  { bank: 'UBS', date: new Date('2026-02-10'), label: 'Internal Deadline' },
  { bank: 'Morgan Stanley', date: new Date('2026-02-15'), label: 'SEC Deadline' },
  { bank: 'JPMorgan', date: new Date('2026-03-15'), label: 'Unknown Authority' },
]

const TIMELINE_EVENTS = [
  { date: 'January 23', event: 'Silver breaks $102. 5 banks technically insolvent. Covering accelerates.', price: '$102.91', current: true },
  { date: 'January 25-26', event: 'UBS margin call failure likely. Swiss regulator emergency consultation.', price: '$120-130' },
  { date: 'January 27-28', event: 'HSBC margin call failure. UK Treasury alerted. MS stress acute.', price: '$140-160' },
  { date: 'January 31', event: 'HSBC internal deadline. First official bank failure?', price: '$180-200' },
  { date: 'February 1', event: 'Citigroup DOJ deadline. Criminal charges possible.', price: '$190-210' },
  { date: 'February 3-5', event: 'JPMorgan liquidity crisis. "Too Big To Fail" invoked.', price: '$220-250' },
  { date: 'February 15-17', event: 'MS SEC deadline. Form SHO filings reveal all positions.', price: '$330-400' },
  { date: 'March 15', event: 'JPMorgan deadline. Mega-merger or nationalization.', price: '$600-1,000+' },
]

const PRICE_TARGETS = [
  { scenario: 'MS covers alone', target: '$289' },
  { scenario: 'MS + Citi cover', target: '$400-500' },
  { scenario: '+ HSBC covers', target: '$700-900' },
  { scenario: '+ UBS covers', target: '$1,200-1,500' },
  { scenario: 'All banks cover', target: '$2,000-3,000+' },
  { scenario: 'COMEX default', target: 'Price breaks' },
]

const MARKET_DATA = [
  { asset: 'Silver', change: '+5.97%', positive: true, signal: 'Squeeze' },
  { asset: 'PSLV', change: '+5.37%', positive: true, signal: 'Physical demand' },
  { asset: 'Goldman Sachs', change: '-3.67%', positive: false, signal: 'Worst' },
  { asset: 'Morgan Stanley', change: '-2.16%', positive: false, signal: 'Heavy selling' },
  { asset: 'JPMorgan', change: '-1.88%', positive: false, signal: 'Declining' },
  { asset: 'SPY', change: '-0.05%', positive: null, signal: 'Flat' },
]

export default function CrisisDashboardPage() {
  const [silverPrice] = useState(102.91)
  const [countdowns, setCountdowns] = useState<Record<string, number>>({})

  useEffect(() => {
    const updateCountdowns = () => {
      const now = new Date()
      const newCountdowns: Record<string, number> = {}
      DEADLINES.forEach(d => {
        const diff = d.date.getTime() - now.getTime()
        newCountdowns[d.bank] = Math.ceil(diff / (1000 * 60 * 60 * 24))
      })
      setCountdowns(newCountdowns)
    }

    updateCountdowns()
    const interval = setInterval(updateCountdowns, 60000)
    return () => clearInterval(interval)
  }, [])

  const insolventCount = BANK_DATA.filter(b => silverPrice >= b.triggerPrice).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f3460] text-[#e8e8e8]">
      {/* Header */}
      <header className="text-center py-8 border-b-2 border-red-500 mb-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center mb-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Main Dashboard</span>
            </Link>
            <Link
              href="/deep-dive"
              className="text-amber-400 hover:text-amber-300 transition-colors"
            >
              Read Full Report
            </Link>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-red-500 mb-2" style={{ textShadow: '0 0 20px rgba(233, 69, 96, 0.5)' }}>
            FAULT.WATCH
          </h1>
          <p className="text-gray-400 text-lg">Bank Silver Short Crisis - Real-Time Monitoring</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4">
        {/* Alert Banner */}
        <motion.div
          className="bg-gradient-to-r from-red-500 to-red-400 text-white py-4 px-6 rounded-xl mb-8 text-center font-bold"
          animate={{ opacity: [1, 0.8, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <AlertTriangle className="inline-block w-5 h-5 mr-2" />
          CRITICAL ALERT: {insolventCount} of 6 monitored banks are TECHNICALLY INSOLVENT at current silver prices
        </motion.div>

        {/* Update Time */}
        <p className="text-right text-gray-400 text-sm mb-6">
          Last Updated: January 23, 2026 - 2:00 PM EST | Silver Price Auto-Updates Every 60 Seconds
        </p>

        {/* Silver Price */}
        <motion.div
          className="bg-gradient-to-br from-[#2d3436] to-[#636e72] border-4 border-gray-300/50 rounded-2xl p-8 text-center mb-8"
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          style={{ boxShadow: '0 10px 40px rgba(192, 192, 192, 0.3)' }}
        >
          <div className="flex items-center justify-center gap-2 mb-2">
            <Zap className="w-6 h-6 text-gray-400" />
            <h2 className="text-gray-300 text-xl">SPOT SILVER PRICE</h2>
          </div>
          <div className="text-6xl md:text-7xl font-bold text-white mb-2" style={{ textShadow: '0 0 30px rgba(192, 192, 192, 0.8)' }}>
            ${silverPrice.toFixed(2)}
          </div>
          <div className="text-2xl text-green-400 flex items-center justify-center gap-2">
            <TrendingUp className="w-6 h-6" />
            +$5.80 (+5.97%) today
          </div>
        </motion.div>

        {/* Total Exposure */}
        <div className="bg-gradient-to-br from-[#2d3436] to-black border-2 border-red-500 rounded-2xl p-8 text-center mb-8">
          <h2 className="text-red-500 text-xl mb-4">COMBINED NET SHORT EXPOSURE</h2>
          <div className="text-5xl md:text-6xl font-bold text-red-400 mb-2" style={{ textShadow: '0 0 30px rgba(255, 71, 87, 0.5)' }}>
            28.85 BILLION OZ
          </div>
          <p className="text-gray-400 text-lg">Across 6 Major Global Banks</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-white/10">
            <div className="text-center">
              <div className="text-3xl font-bold text-amber-400">36x</div>
              <div className="text-sm text-gray-400">Annual Global Production</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-amber-400">962x</div>
              <div className="text-sm text-gray-400">COMEX Registered Inventory</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-amber-400">$657B+</div>
              <div className="text-sm text-gray-400">Tier 1 Capital Already Wiped</div>
            </div>
          </div>
        </div>

        {/* Countdown Section */}
        <div className="bg-red-500/10 border-2 border-red-500 rounded-2xl p-6 mb-8">
          <h3 className="text-red-500 text-center text-xl font-bold mb-6 flex items-center justify-center gap-2">
            <Clock className="w-5 h-5" />
            COUNTDOWN TO DEADLINES
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {DEADLINES.map((d) => (
              <div key={d.bank} className="bg-black/30 rounded-xl p-4 text-center">
                <div className="text-sm text-gray-300 mb-1">{d.bank}</div>
                <div className="text-4xl font-bold text-red-400">{countdowns[d.bank] || '...'}</div>
                <div className="text-xs text-gray-500 mt-1">{d.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Insolvency Status */}
          <Card title="INSOLVENCY STATUS" icon={<Skull className="w-5 h-5" />}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-gray-400 font-normal">Bank</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Trigger Price</th>
                  <th className="text-center py-2 text-gray-400 font-normal">Status</th>
                </tr>
              </thead>
              <tbody>
                {BANK_DATA.map((bank) => (
                  <tr key={bank.name} className="border-b border-white/5">
                    <td className="py-3">{bank.name}</td>
                    <td className="py-3 text-right">${bank.triggerPrice.toFixed(2)}</td>
                    <td className="py-3 text-center">
                      {bank.solvent ? (
                        <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">SOLVENT</span>
                      ) : (
                        <span className="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">INSOLVENT</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Position Sizes */}
          <Card title="POSITION SIZES (Alleged)" icon={<DollarSign className="w-5 h-5" />}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-gray-400 font-normal">Bank</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Net Short</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Entry Est.</th>
                </tr>
              </thead>
              <tbody>
                {BANK_DATA.map((bank) => (
                  <tr key={bank.name} className="border-b border-white/5">
                    <td className="py-3">{bank.name}</td>
                    <td className="py-3 text-right text-red-400">{bank.shortPos}</td>
                    <td className="py-3 text-right">{bank.entry}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Current Losses */}
          <Card title={`CURRENT LOSSES @ $${silverPrice}`} icon={<TrendingDown className="w-5 h-5" />}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-gray-400 font-normal">Bank</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Loss</th>
                  <th className="text-right py-2 text-gray-400 font-normal">vs Tier 1</th>
                </tr>
              </thead>
              <tbody>
                {BANK_DATA.map((bank) => (
                  <tr key={bank.name} className="border-b border-white/5">
                    <td className="py-3">{bank.name}</td>
                    <td className={`py-3 text-right font-bold ${bank.solvent ? '' : 'text-red-400'}`}>{bank.loss}</td>
                    <td className="py-3 text-right">{bank.wipeout} {bank.solvent ? '(buffer)' : 'wiped'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Days to Cash Exhaustion */}
          <Card title="DAYS TO CASH EXHAUSTION" icon={<Clock className="w-5 h-5" />}>
            <p className="text-gray-400 text-xs mb-4">Assuming $10/day silver rise + operating expenses</p>
            <div className="space-y-4">
              {BANK_DATA.map((bank) => (
                <div key={bank.name}>
                  <div className="flex justify-between mb-1">
                    <span>{bank.name}</span>
                    <span className={bank.solvent ? 'text-green-400' : bank.exhaustPercent > 70 ? 'text-red-400' : 'text-amber-400'}>
                      {bank.daysToExhaust} days
                    </span>
                  </div>
                  <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        bank.solvent ? 'bg-gradient-to-r from-green-500 to-green-400' :
                        bank.exhaustPercent > 70 ? 'bg-gradient-to-r from-red-500 to-red-400' :
                        'bg-gradient-to-r from-amber-500 to-amber-400'
                      }`}
                      initial={{ width: 0 }}
                      animate={{ width: `${bank.exhaustPercent}%` }}
                      transition={{ duration: 1, delay: 0.2 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Timeline */}
        <Card title="PROJECTED CASCADE TIMELINE" icon={<Calendar className="w-5 h-5" />} className="mb-8">
          <div className="relative pl-8">
            <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gradient-to-b from-red-500 via-amber-500 to-amber-600" />

            {TIMELINE_EVENTS.map((event, i) => (
              <div key={i} className="relative pb-6 last:pb-0">
                <div className={`absolute -left-5 top-1 w-4 h-4 rounded-full border-2 border-[#1a1a2e] ${
                  event.current ? 'bg-amber-500 shadow-lg shadow-amber-500/50' : 'bg-red-500'
                }`} />
                <div className="ml-4">
                  <div className="text-red-400 text-sm mb-1">
                    {event.date} {event.current && <span className="text-amber-400">(TODAY)</span>}
                  </div>
                  <div className="text-white">{event.event}</div>
                  <div className="text-gray-400 text-sm mt-1">Silver est: {event.price}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Price Targets */}
          <Card title="SILVER PRICE TARGETS" icon={<Target className="w-5 h-5" />}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-gray-400 font-normal">Scenario</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Price Target</th>
                </tr>
              </thead>
              <tbody>
                {PRICE_TARGETS.map((pt, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-3">{pt.scenario}</td>
                    <td className="py-3 text-right text-amber-400 font-bold">{pt.target}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Market Correlations */}
          <Card title="MARKET CORRELATIONS TODAY" icon={<BarChart3 className="w-5 h-5" />}>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-gray-400 font-normal">Asset</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Change</th>
                  <th className="text-right py-2 text-gray-400 font-normal">Signal</th>
                </tr>
              </thead>
              <tbody>
                {MARKET_DATA.map((m, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-3">{m.asset}</td>
                    <td className={`py-3 text-right ${m.positive === true ? 'text-green-400' : m.positive === false ? 'text-red-400' : 'text-gray-400'}`}>
                      {m.change}
                    </td>
                    <td className="py-3 text-right">
                      {m.positive === true && <span className="text-green-400">+</span>}
                      {m.positive === false && <span className="text-amber-400">!</span>}
                      {m.positive === null && <span className="text-green-400">ok</span>}
                      {' '}{m.signal}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="text-amber-400 text-sm mt-4">
              <Zap className="inline w-4 h-4 mr-1" />
              Banks bleeding while market flat = sector-specific crisis
            </p>
          </Card>
        </div>

        {/* Disclaimer */}
        <div className="bg-amber-500/10 border border-amber-500 rounded-xl p-6 mb-8">
          <h4 className="text-amber-400 font-bold mb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            IMPORTANT DISCLAIMER
          </h4>
          <p className="text-gray-400 text-sm">
            This analysis is based on a combination of publicly available data, leaked documents, unverified rumors from financial sources, and mathematical modeling. Position sizes and entry prices cannot be independently verified. All banks mentioned deny having problematic silver exposure. This is NOT financial advice. Conduct your own due diligence before making any investment decisions. The operators of this site may hold positions in securities and commodities mentioned.
          </p>
        </div>

        {/* Footer */}
        <footer className="text-center py-8 border-t border-white/10">
          <p className="font-bold text-white mb-2">FAULT.WATCH</p>
          <p className="text-gray-400 mb-4">Monitoring Systemic Risk in Real-Time</p>
          <p className="text-gray-500 text-sm italic mb-2">
            "The market can remain irrational longer than you can remain solvent." - Keynes
          </p>
          <p className="text-gray-500 text-sm italic mb-6">
            "But the market cannot remain irrational longer than the silver can remain undelivered." - Fault.Watch
          </p>
          <p className="text-gray-600 text-xs">
            Report Version 1.0 | Data as of January 23, 2026
          </p>
          <div className="mt-6">
            <Link
              href="/deep-dive"
              className="inline-flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-xl font-bold transition-colors"
            >
              Read Full Analysis Report
            </Link>
          </div>
        </footer>
      </div>
    </div>
  )
}

function Card({ title, icon, children, className = '' }: {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={`bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 ${className}`}>
      <h3 className="text-red-500 font-bold mb-4 pb-3 border-b border-red-500/30 flex items-center gap-2">
        {icon}
        {title}
      </h3>
      {children}
    </div>
  )
}
