'use client'

import { motion } from 'framer-motion'
import { CrisisGauge } from './CrisisGauge'
import { KeyStats, createKeyStats } from './KeyStats'
import { LiveTicker } from './LiveTicker'
import { DashboardData } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

interface HeroSectionProps {
  dashboard: DashboardData
}

export function HeroSection({ dashboard }: HeroSectionProps) {
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
    <section className="relative min-h-[80vh] flex flex-col">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-red-950/20 via-black to-black pointer-events-none" />

      {/* Radial glow behind gauge */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full opacity-20"
        style={{
          background: `radial-gradient(circle, ${crisisPercentage >= 60 ? 'rgba(220,38,38,0.4)' : 'rgba(245,158,11,0.3)'} 0%, transparent 70%)`
        }}
      />

      {/* Header */}
      <header className="relative z-10 border-b border-gray-800 bg-black/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-black text-white tracking-tight">
              fault<span className="text-red-500">.</span>watch
            </h1>
            <span className="px-2 py-1 bg-red-500/20 text-red-400 text-[10px] font-bold rounded uppercase tracking-wider">
              LIVE
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span>Last updated: {new Date(dashboard.last_updated).toLocaleTimeString()}</span>
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
