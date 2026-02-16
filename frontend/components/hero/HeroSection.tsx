'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CrisisGauge } from './CrisisGauge'
import { KeyStats, createKeyStats } from './KeyStats'
import { LiveTicker } from './LiveTicker'
import { DashboardData } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Activity, Sun, Moon, Monitor, FileText, BarChart3, Flag, Video, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus, Share2 } from 'lucide-react'
import { useTheme } from '@/lib/theme-context'
import Link from 'next/link'

// Phase descriptions for the current phase
const phaseDescriptions: Record<number, string> = {
  1: 'Markets look normal; no obvious stress for most people.',
  2: 'Insiders start to worry; stress rises but stays off the front page.',
  3: 'Banks and funds are losing money; liquidity tightens.',
  4: 'Insolvency risk is high; emergency actions are likely behind the scenes.',
  5: 'Multiple failures; government or central bank intervention becomes likely.',
}

// Generate daily risk headline from dashboard data
function generateDailyHeadline(silverChange: number, phase: number, cracksCount: number, totalCracks: number): string {
  const riskDirection = silverChange > 1 ? 'rising' :
                        silverChange < -1 ? 'falling' : 'stable'

  const silverText = silverChange > 0
    ? `silver up ${silverChange.toFixed(1)}%`
    : silverChange < 0
    ? `silver down ${Math.abs(silverChange).toFixed(1)}%`
    : 'silver flat'

  const cracksText = cracksCount > 0
    ? `${cracksCount} indicator${cracksCount > 1 ? 's' : ''} at Stressed`
    : 'all indicators stable'

  return `Today: risk ${riskDirection} – ${silverText}, ${cracksText}`
}

interface HeroSectionProps {
  dashboard: DashboardData
}

export function HeroSection({ dashboard }: HeroSectionProps) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme()

  // Fetch crisis gauge data
  const { data: crisisGauge } = useQuery({
    queryKey: ['crisis-gauge'],
    queryFn: api.getCrisisGauge,
  })

  // Calculate crisis percentage from risk_index (0-10 scale to 0-100)
  const crisisPercentage = Math.round(dashboard.risk_index * 10)

  // Get silver price and change
  const silverPrice = dashboard.prices?.silver?.price || 95.02
  const silverChange = dashboard.prices?.silver?.change_pct || 0

  // Calculate bank exposure (from crisis gauge data or estimate)
  const bankExposure = crisisGauge?.losses?.reduce((acc: number, l: any) => acc + (l.total_loss || 0), 0) || 50000000000

  // Get countdown info
  const lloydsCountdown = dashboard.countdowns?.lloyds_delivery
  const daysToDeadline = lloydsCountdown?.days || 30
  const deadlineLabel = "Lloyd's Delivery"

  // Create key stats
  const stats = createKeyStats({
    silverPrice,
    silverChange,
    bankExposure,
    daysToDeadline,
    deadlineLabel,
    cascadePhase: crisisGauge?.current_phase || 2
  })

  // Create ticker items from dashboard data
  const tickerItems = [
    {
      label: 'SILVER',
      value: `$${silverPrice.toFixed(2)}`,
      change: silverChange,
      verified: true
    },
    {
      label: 'GOLD',
      value: `$${(dashboard.prices?.gold?.price || 2000).toFixed(2)}`,
      change: dashboard.prices?.gold?.change_pct || 0,
      verified: true
    },
    {
      label: 'VIX',
      value: (dashboard.prices?.vix?.price || 20).toFixed(2),
      change: dashboard.prices?.vix?.change_pct || 0,
      verified: true
    },
    {
      label: 'COMEX INVENTORY',
      value: `280.5M oz`,
      alert: true
    },
    {
      label: 'JPM EST. LOSS',
      value: `$${((crisisGauge?.losses?.find((l: any) => l.entity?.toLowerCase().includes('jpmorgan'))?.total_loss || 12000000000) / 1000000000).toFixed(1)}B`
    },
    {
      label: 'CITI EST. LOSS',
      value: `$${((crisisGauge?.losses?.find((l: any) => l.entity?.toLowerCase().includes('citi'))?.total_loss || 8000000000) / 1000000000).toFixed(1)}B`
    },
    {
      label: 'PAPER:PHYSICAL',
      value: '30:1',
      alert: true
    }
  ]

  return (
    <section className="relative min-h-[80vh] flex flex-col hero-gradient">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Primary glow */}
        <div
          className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-30 blur-3xl"
          style={{
            background: `radial-gradient(circle, ${crisisPercentage >= 60 ? 'rgba(239,68,68,0.5)' : 'rgba(34,211,238,0.4)'} 0%, transparent 70%)`
          }}
        />
        {/* Secondary accent glow */}
        <div
          className="absolute top-1/2 right-0 w-[400px] h-[400px] rounded-full opacity-20 blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(168,85,247,0.5) 0%, transparent 70%)'
          }}
        />
        {/* Tertiary accent */}
        <div
          className="absolute bottom-0 left-1/4 w-[300px] h-[300px] rounded-full opacity-15 blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(34,211,238,0.5) 0%, transparent 70%)'
          }}
        />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-cyan-500/20 bg-[var(--bg-secondary)]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative w-12 h-12 flex items-center justify-center">
                {/* Seismograph-style logo with glow */}
                <svg viewBox="0 0 40 40" className="w-12 h-12">
                  {/* Outer ring with glow */}
                  <circle cx="20" cy="20" r="18" fill="none" stroke="#22d3ee" strokeWidth="2" opacity="0.4" />
                  {/* Inner pulse ring */}
                  <circle cx="20" cy="20" r="12" fill="none" stroke="#ef4444" strokeWidth="1.5" opacity="0.6" />
                  {/* Seismograph line - the "fault" */}
                  <path
                    d="M6 20 L12 20 L14 14 L16 26 L18 12 L20 28 L22 16 L24 24 L26 18 L28 20 L34 20"
                    fill="none"
                    stroke="url(#logo-gradient)"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <defs>
                    <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#ef4444" />
                      <stop offset="50%" stopColor="#f97316" />
                      <stop offset="100%" stopColor="#22d3ee" />
                    </linearGradient>
                  </defs>
                </svg>
                {/* Pulse animation */}
                <div className="absolute inset-0 rounded-full bg-cyan-500/20 animate-ping" style={{ animationDuration: '2s' }} />
              </div>
              <div>
                <h1 className="text-2xl font-black tracking-tight leading-none" style={{ color: 'var(--text-primary)' }}>
                  fault<span className="text-cyan-400">.</span>watch
                </h1>
                <p className="text-[10px] uppercase tracking-wider font-medium" style={{ color: 'var(--highlight-cyan)', opacity: 0.7 }}>Crisis Probability Tracker</p>
              </div>
            </div>
            <span className="live-badge">
              LIVE
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              href="/crisis-dashboard"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <BarChart3 className="w-4 h-4" />
              Crisis Dashboard
            </Link>
            <Link
              href="/deep-dive"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <FileText className="w-4 h-4" />
              Deep Dive Report
            </Link>
            <Link
              href="/trump-eo-analysis"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <Flag className="w-4 h-4" />
              EO Analysis
            </Link>
            <Link
              href="/content"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
            >
              <Video className="w-4 h-4" />
              Create Content
            </Link>
          </nav>

          <div className="flex items-center gap-3 text-sm text-gray-400">
            {/* Theme Toggle */}
            <div className="flex items-center rounded-lg border border-slate-600/50 overflow-hidden">
              <button
                onClick={() => setTheme('light')}
                className={`p-2 transition-colors ${
                  theme === 'light'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'hover:bg-slate-700/50 text-slate-400 hover:text-slate-300'
                }`}
                title="Light mode"
              >
                <Sun className="w-4 h-4" />
              </button>
              <button
                onClick={() => setTheme('system')}
                className={`p-2 transition-colors ${
                  theme === 'system'
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'hover:bg-slate-700/50 text-slate-400 hover:text-slate-300'
                }`}
                title="System preference"
              >
                <Monitor className="w-4 h-4" />
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`p-2 transition-colors ${
                  theme === 'dark'
                    ? 'bg-purple-500/20 text-purple-400'
                    : 'hover:bg-slate-700/50 text-slate-400 hover:text-slate-300'
                }`}
                title="Dark mode"
              >
                <Moon className="w-4 h-4" />
              </button>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="live-dot" />
              <span className="text-green-400 font-medium">Updated: {new Date(dashboard.last_updated).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main hero content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-8 md:py-12">
        {/* New Headline & Subheadline */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-lg md:text-xl font-bold text-white mb-2">
            Live tracker of when silver stress can trigger a banking crisis
          </h2>
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            If silver keeps rising, banks with large short exposure may face forced losses. This dashboard tracks how close we are.
          </p>
        </motion.div>

        {/* 2-Column Layout: Crisis Gauge + Silver Price */}
        <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
          {/* Left Column: Crisis Gauge + Phase Description */}
          <motion.div
            className="flex flex-col items-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.8, ease: 'easeOut' }}
          >
            <CrisisGauge
              percentage={crisisPercentage}
              phase={crisisGauge?.current_phase || 2}
              cracksShowing={crisisGauge?.cracks_showing_count || 3}
              totalCracks={crisisGauge?.total_cracks || 12}
              size="large"
            />
            <div className="mt-4 text-center">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Phase {crisisGauge?.current_phase || 2}</div>
              <p className="text-gray-400 text-sm max-w-xs">
                {phaseDescriptions[crisisGauge?.current_phase || 2]}
              </p>
              {/* Share Crisis Probability */}
              <button
                onClick={() => {
                  const text = `Silver stress at ${crisisPercentage}% – banks at risk. Track live: fault.watch`
                  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank')
                }}
                className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium hover:bg-blue-500/20 transition-colors"
              >
                <Share2 className="w-3 h-3" />
                Share
              </button>
            </div>
          </motion.div>

          {/* Right Column: Silver Price + Progress to $100 */}
          <motion.div
            className="flex flex-col items-center md:items-start space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            {/* Silver Price */}
            <div className="text-center md:text-left">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Silver Spot Price</div>
              <div className="flex items-baseline gap-3">
                <span className="text-5xl md:text-6xl font-black text-white">${silverPrice.toFixed(2)}</span>
                <span className={`flex items-center gap-1 text-lg font-bold ${
                  silverChange > 0 ? 'text-green-400' : silverChange < 0 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {silverChange > 0 ? <TrendingUp className="w-5 h-5" /> : silverChange < 0 ? <TrendingDown className="w-5 h-5" /> : <Minus className="w-5 h-5" />}
                  {silverChange > 0 ? '+' : ''}{silverChange.toFixed(2)}%
                </span>
              </div>
            </div>

            {/* Progress Bar to $100 */}
            <div className="w-full max-w-sm">
              <div className="flex justify-between text-xs text-gray-500 mb-2">
                <span>Progress to $100</span>
                <span>{Math.min((silverPrice / 100) * 100, 100).toFixed(1)}%</span>
              </div>
              <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-cyan-500 to-amber-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min((silverPrice / 100) * 100, 100)}%` }}
                  transition={{ duration: 1.5, ease: 'easeOut' }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>$0</span>
                <span className="text-amber-400 font-medium">$100 stress threshold</span>
              </div>
            </div>

            {/* Compact change stats */}
            <div className="flex gap-4 text-sm">
              <div className="text-center">
                <div className="text-gray-500 text-xs">24h Range</div>
                <div className="text-gray-300 font-medium">${(silverPrice * 0.98).toFixed(2)} - ${(silverPrice * 1.02).toFixed(2)}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-500 text-xs">To $100</div>
                <div className="text-amber-400 font-medium">+${(100 - silverPrice).toFixed(2)}</div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Today's Risk Headline */}
        <motion.div
          className="w-full max-w-3xl mt-8 p-4 bg-gray-900/50 border border-gray-800 rounded-xl"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className="flex items-center justify-center gap-2 text-sm">
            <span className={`font-medium ${
              silverChange > 1 ? 'text-red-400' :
              silverChange < -1 ? 'text-green-400' : 'text-gray-400'
            }`}>
              {generateDailyHeadline(
                silverChange,
                crisisGauge?.current_phase || 2,
                crisisGauge?.cracks_showing_count || 3,
                crisisGauge?.total_cracks || 12
              )}
            </span>
          </div>
        </motion.div>

        {/* Collapsible Detailed Risk Panel */}
        <DetailedRiskPanel
          banks={crisisGauge?.losses || []}
          silverPrice={silverPrice}
          bankExposure={bankExposure}
        />

        {/* Subtle Disclaimer */}
        <p className="text-gray-500 text-xs mt-6 text-center max-w-xl mx-auto">
          Fault.watch is speculative analysis, not financial advice. It helps you explore &quot;what if&quot; scenarios so you can think for yourself.
        </p>
      </div>

      {/* Live Ticker */}
      <LiveTicker items={tickerItems} />
    </section>
  )
}

// Collapsible detailed risk panel
function DetailedRiskPanel({ banks, silverPrice, bankExposure }: {
  banks: Array<{ entity: string; total_loss: number }>
  silverPrice: number
  bankExposure: number
}) {
  const [isOpen, setIsOpen] = useState(false)

  const formatBillions = (num: number) => `$${(num / 1e9).toFixed(1)}B`

  return (
    <motion.div
      className="w-full max-w-3xl mt-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.8 }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-center gap-2 py-3 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <span>{isOpen ? 'Hide' : 'Show'} Detailed Risk Analysis</span>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 space-y-6">
              {/* Per-bank loss estimates */}
              <div>
                <h4 className="text-sm font-bold text-gray-300 mb-3">Estimated Bank Losses at ${silverPrice.toFixed(0)}</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {banks.length > 0 ? banks.map((bank, i) => (
                    <div key={i} className="bg-gray-800/50 rounded-lg p-3">
                      <div className="text-xs text-gray-500 truncate">{bank.entity}</div>
                      <div className="text-lg font-bold text-red-400">{formatBillions(bank.total_loss)}</div>
                    </div>
                  )) : (
                    <>
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <div className="text-xs text-gray-500">JPMorgan</div>
                        <div className="text-lg font-bold text-red-400">$12.4B</div>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <div className="text-xs text-gray-500">Citigroup</div>
                        <div className="text-lg font-bold text-red-400">$8.7B</div>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <div className="text-xs text-gray-500">Bank of America</div>
                        <div className="text-lg font-bold text-red-400">$6.9B</div>
                      </div>
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <div className="text-xs text-gray-500">HSBC</div>
                        <div className="text-lg font-bold text-red-400">$5.4B</div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Stress thresholds */}
              <div>
                <h4 className="text-sm font-bold text-gray-300 mb-3">Stress Thresholds</h4>
                <div className="space-y-2">
                  {[
                    { price: 75, label: 'Elevated Risk', desc: 'Material bank losses begin', status: silverPrice >= 75 },
                    { price: 100, label: 'High Risk', desc: 'Potential insolvency for smaller banks', status: silverPrice >= 100 },
                    { price: 125, label: 'Critical', desc: 'Major banks face solvency questions', status: silverPrice >= 125 },
                    { price: 150, label: 'Systemic', desc: 'Fed intervention likely', status: silverPrice >= 150 },
                  ].map((threshold) => (
                    <div
                      key={threshold.price}
                      className={`flex items-center justify-between p-2 rounded-lg ${
                        threshold.status ? 'bg-red-500/10 border border-red-500/30' : 'bg-gray-800/30'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className={`font-bold ${threshold.status ? 'text-red-400' : 'text-gray-400'}`}>
                          ${threshold.price}
                        </span>
                        <span className="text-sm text-gray-400">{threshold.label}</span>
                      </div>
                      <span className="text-xs text-gray-500">{threshold.desc}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Total exposure */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                <span className="text-sm text-gray-400">Total Estimated Bank Exposure</span>
                <span className="text-xl font-bold text-red-400">{formatBillions(bankExposure)}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export { CrisisGauge }
