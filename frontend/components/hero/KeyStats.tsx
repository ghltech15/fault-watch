'use client'

import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Clock, Building2, Layers, AlertTriangle } from 'lucide-react'
import { Sparkline, generateMockPriceData } from '@/components/engagement/Sparkline'

interface StatItem {
  label: string
  value: string | number
  change?: number
  prefix?: string
  suffix?: string
  icon: React.ReactNode
  color?: string
  subtext?: string
  showSparkline?: boolean
}

interface KeyStatsProps {
  stats: StatItem[]
}

function AnimatedNumber({ value, prefix = '', suffix = '' }: { value: number; prefix?: string; suffix?: string }) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    const duration = 1500
    const startTime = Date.now()
    const startValue = display

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = startValue + (value - startValue) * eased

      setDisplay(current)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [value])

  const formatNumber = (num: number) => {
    if (num >= 1e12) return `${(num / 1e12).toFixed(1)}T`
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`
    return num.toFixed(2)
  }

  return (
    <span className="tabular-nums">
      {prefix}{formatNumber(display)}{suffix}
    </span>
  )
}

function StatCard({ stat, index }: { stat: StatItem; index: number }) {
  const isNumeric = typeof stat.value === 'number'
  const colorClass = stat.color || 'text-white'

  // Generate mock sparkline data (in production, this would come from API)
  const sparklineData = useMemo(() => {
    if (!stat.showSparkline || !isNumeric) return null
    return generateMockPriceData(stat.value as number, 14, 0.015)
  }, [stat.showSparkline, stat.value, isNumeric])

  return (
    <motion.div
      className="relative bg-gray-900/50 border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-colors"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
    >
      {/* Icon */}
      <div className="flex items-center justify-between mb-3">
        <div className={`p-2 rounded-lg bg-gray-800/50 ${colorClass}`}>
          {stat.icon}
        </div>
        {stat.change !== undefined && (
          <div
            className={`flex items-center gap-1 text-sm font-bold ${
              stat.change > 0 ? 'text-green-400' : stat.change < 0 ? 'text-red-400' : 'text-gray-400'
            }`}
          >
            {stat.change > 0 ? <TrendingUp className="w-4 h-4" /> : stat.change < 0 ? <TrendingDown className="w-4 h-4" /> : null}
            {stat.change > 0 ? '+' : ''}{stat.change.toFixed(2)}%
          </div>
        )}
      </div>

      {/* Value with optional sparkline */}
      <div className="flex items-end justify-between gap-2">
        <div>
          <div className={`text-3xl md:text-4xl font-black mb-1 ${colorClass}`}>
            {isNumeric ? (
              <AnimatedNumber value={stat.value as number} prefix={stat.prefix} suffix={stat.suffix} />
            ) : (
              <span>{stat.prefix}{stat.value}{stat.suffix}</span>
            )}
          </div>

          {/* Label */}
          <div className="text-xs text-gray-400 uppercase tracking-wider font-medium">
            {stat.label}
          </div>
        </div>

        {/* Sparkline */}
        {sparklineData && (
          <div className="flex-shrink-0">
            <Sparkline
              data={sparklineData}
              width={60}
              height={28}
              color="auto"
              showArea
            />
            <div className="text-[9px] text-gray-600 text-right mt-0.5">14d</div>
          </div>
        )}
      </div>

      {/* Subtext */}
      {stat.subtext && (
        <div className="text-xs text-gray-500 mt-1">
          {stat.subtext}
        </div>
      )}
    </motion.div>
  )
}

export function KeyStats({ stats }: KeyStatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <StatCard key={stat.label} stat={stat} index={index} />
      ))}
    </div>
  )
}

// Helper function to create common stats
export function createKeyStats(data: {
  silverPrice: number
  silverChange: number
  bankExposure: number
  daysToDeadline: number
  deadlineLabel: string
  cascadePhase: number
}) {
  return [
    {
      label: 'Silver Spot',
      value: data.silverPrice,
      change: data.silverChange,
      prefix: '$',
      icon: <Layers className="w-5 h-5" />,
      color: 'text-gray-100',
      showSparkline: true
    },
    {
      label: 'Bank Exposure',
      value: data.bankExposure,
      prefix: '$',
      icon: <Building2 className="w-5 h-5" />,
      color: 'text-red-400',
      subtext: 'Est. short positions',
      showSparkline: true
    },
    {
      label: data.deadlineLabel,
      value: data.daysToDeadline,
      suffix: ' days',
      icon: <Clock className="w-5 h-5" />,
      color: data.daysToDeadline < 7 ? 'text-red-400' : data.daysToDeadline < 30 ? 'text-amber-400' : 'text-gray-100'
    },
    {
      label: 'Cascade Stage',
      value: `${data.cascadePhase}/5`,
      icon: <AlertTriangle className="w-5 h-5" />,
      color: data.cascadePhase >= 4 ? 'text-red-400' : data.cascadePhase >= 3 ? 'text-amber-400' : 'text-gray-100',
      subtext: data.cascadePhase >= 4 ? 'CRITICAL' : data.cascadePhase >= 3 ? 'WARNING' : 'STABLE'
    }
  ]
}
