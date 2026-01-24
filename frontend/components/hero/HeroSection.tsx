'use client'

import { motion } from 'framer-motion'
import { CrisisGauge } from './CrisisGauge'
import { KeyStats, createKeyStats } from './KeyStats'
import { LiveTicker } from './LiveTicker'
import { DashboardData } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Activity, Sun, Moon, Monitor, FileText, BarChart3, Flag } from 'lucide-react'
import { useTheme } from '@/lib/theme-context'
import Link from 'next/link'

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
        {/* Title */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-sm md:text-base font-bold text-gray-400 uppercase tracking-[0.3em] mb-2">
            Systemic Banking Risk Monitor
          </h2>
          <p className="text-gray-500 text-sm max-w-xl mx-auto">
            Real-time tracking of precious metals short exposure and potential bank insolvency
          </p>
        </motion.div>

        {/* Crisis Gauge */}
        <motion.div
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
        </motion.div>

        {/* Key Stats */}
        <div className="w-full max-w-4xl mt-12">
          <KeyStats stats={stats} />
        </div>
      </div>

      {/* Live Ticker */}
      <LiveTicker items={tickerItems} />
    </section>
  )
}

export { CrisisGauge }
