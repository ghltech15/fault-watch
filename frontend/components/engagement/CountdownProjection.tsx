'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Clock, TrendingUp, Target, AlertTriangle } from 'lucide-react'

interface CountdownProjectionProps {
  currentPrice: number
  targetPrice: number
  dailyChangePercent: number
  label: string
}

export function CountdownProjection({
  currentPrice,
  targetPrice,
  dailyChangePercent,
  label
}: CountdownProjectionProps) {
  const [daysToTarget, setDaysToTarget] = useState<number | null>(null)
  const [confidence, setConfidence] = useState<'high' | 'medium' | 'low'>('medium')

  useEffect(() => {
    if (currentPrice >= targetPrice) {
      setDaysToTarget(0)
      return
    }

    if (dailyChangePercent <= 0) {
      setDaysToTarget(null) // Price going down, can't project
      return
    }

    // Calculate days to target based on compound growth
    // Using: targetPrice = currentPrice * (1 + dailyRate)^days
    // days = ln(targetPrice/currentPrice) / ln(1 + dailyRate)
    const dailyRate = dailyChangePercent / 100
    const priceRatio = targetPrice / currentPrice
    const days = Math.ceil(Math.log(priceRatio) / Math.log(1 + dailyRate))

    setDaysToTarget(Math.min(days, 365)) // Cap at 1 year

    // Set confidence based on volatility and distance
    if (days < 30 && dailyChangePercent > 1) {
      setConfidence('high')
    } else if (days < 90) {
      setConfidence('medium')
    } else {
      setConfidence('low')
    }
  }, [currentPrice, targetPrice, dailyChangePercent])

  if (currentPrice >= targetPrice) {
    return (
      <div className="flex items-center gap-2 text-green-400">
        <Target className="w-4 h-4" />
        <span className="text-sm font-bold">TARGET REACHED</span>
      </div>
    )
  }

  if (daysToTarget === null) {
    return (
      <div className="flex items-center gap-2 text-gray-500">
        <Clock className="w-4 h-4" />
        <span className="text-sm">Projection unavailable</span>
      </div>
    )
  }

  const confidenceColors = {
    high: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    medium: 'text-gray-300 border-gray-700 bg-gray-800/50',
    low: 'text-gray-500 border-gray-800 bg-gray-900/50'
  }

  return (
    <motion.div
      className={`inline-flex items-center gap-3 px-4 py-2 rounded-xl border ${confidenceColors[confidence]}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4" />
        <span className="text-sm">
          <span className="font-bold">${targetPrice}</span> in
        </span>
      </div>

      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-black tabular-nums">{daysToTarget}</span>
        <span className="text-sm">{daysToTarget === 1 ? 'day' : 'days'}</span>
      </div>

      {confidence === 'high' && (
        <TrendingUp className="w-4 h-4 text-green-400" />
      )}

      <span className={`text-[10px] uppercase tracking-wider ${
        confidence === 'high' ? 'text-amber-400' :
        confidence === 'medium' ? 'text-gray-400' : 'text-gray-600'
      }`}>
        {confidence} conf.
      </span>
    </motion.div>
  )
}

// Compact version for inline use
export function MiniCountdown({
  currentPrice,
  targetPrice,
  dailyChangePercent
}: Omit<CountdownProjectionProps, 'label'>) {
  if (currentPrice >= targetPrice) {
    return <span className="text-green-400 text-xs font-bold">REACHED</span>
  }

  if (dailyChangePercent <= 0) {
    return <span className="text-gray-500 text-xs">--</span>
  }

  const dailyRate = dailyChangePercent / 100
  const priceRatio = targetPrice / currentPrice
  const days = Math.ceil(Math.log(priceRatio) / Math.log(1 + dailyRate))

  if (days > 365) {
    return <span className="text-gray-500 text-xs">1y+</span>
  }

  return (
    <span className="text-amber-400 text-xs font-bold tabular-nums">
      ~{days}d
    </span>
  )
}

// Full projection card with multiple targets
export function ProjectionCard({
  currentPrice,
  dailyChangePercent
}: {
  currentPrice: number
  dailyChangePercent: number
}) {
  const targets = [100, 125, 150, 200]

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        <h4 className="font-bold text-white">Price Projections</h4>
        <span className="text-xs text-gray-500 ml-auto">
          Based on {dailyChangePercent.toFixed(2)}%/day
        </span>
      </div>

      <div className="space-y-3">
        {targets.map(target => {
          if (currentPrice >= target) return null

          const dailyRate = dailyChangePercent / 100
          const priceRatio = target / currentPrice
          const days = dailyRate > 0
            ? Math.ceil(Math.log(priceRatio) / Math.log(1 + dailyRate))
            : null

          return (
            <div
              key={target}
              className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
            >
              <div className="flex items-center gap-3">
                <span className="text-xl font-bold text-white">${target}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  target === 100 ? 'bg-amber-500/20 text-amber-400' :
                  target === 150 ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-800 text-gray-400'
                }`}>
                  {target === 100 ? 'SYSTEMIC' :
                   target === 150 ? 'COLLAPSE' :
                   target === 125 ? 'CRITICAL' : 'TARGET'}
                </span>
              </div>

              <div className="text-right">
                {days !== null && days <= 365 ? (
                  <>
                    <div className="text-lg font-bold text-amber-400 tabular-nums">
                      {days} days
                    </div>
                    <div className="text-[10px] text-gray-500">
                      ~{new Date(Date.now() + days * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                  </>
                ) : (
                  <div className="text-sm text-gray-500">
                    {dailyChangePercent <= 0 ? 'N/A' : '1 year+'}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <p className="text-[10px] text-gray-600 mt-4">
        * Projections assume current daily rate continues. Actual timing may vary significantly.
      </p>
    </div>
  )
}
