'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Users, TrendingUp, TrendingDown, Clock, Zap } from 'lucide-react'

interface LiveIndicatorsProps {
  initialSilverPrice?: number
  currentSilverPrice?: number
}

export function LiveIndicators({ initialSilverPrice, currentSilverPrice }: LiveIndicatorsProps) {
  const [viewerCount, setViewerCount] = useState(0)
  const [sessionStartPrice, setSessionStartPrice] = useState<number | null>(null)
  const [sessionDuration, setSessionDuration] = useState(0)
  const [recentActivity, setRecentActivity] = useState<string[]>([])

  // Simulate realistic viewer count (would be real WebSocket in production)
  useEffect(() => {
    // Start with a base count
    const baseCount = 847 + Math.floor(Math.random() * 400)
    setViewerCount(baseCount)

    // Fluctuate viewer count realistically
    const interval = setInterval(() => {
      setViewerCount(prev => {
        const change = Math.floor(Math.random() * 20) - 8 // -8 to +12
        return Math.max(500, Math.min(2000, prev + change))
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Track session start price
  useEffect(() => {
    if (initialSilverPrice && sessionStartPrice === null) {
      setSessionStartPrice(initialSilverPrice)
    }
  }, [initialSilverPrice, sessionStartPrice])

  // Track session duration
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionDuration(prev => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  // Simulate recent activity feed
  useEffect(() => {
    const activities = [
      'Silver price updated',
      'Bank exposure recalculated',
      'COMEX inventory checked',
      'Crisis gauge refreshed',
      'New viewer from California',
      'Alert triggered for 3 users',
      'CDS spreads updated',
      'VIX data refreshed'
    ]

    const interval = setInterval(() => {
      const activity = activities[Math.floor(Math.random() * activities.length)]
      setRecentActivity(prev => [activity, ...prev].slice(0, 3))
    }, 8000)

    return () => clearInterval(interval)
  }, [])

  // Calculate price change since arrival
  const priceChangeSinceArrival = sessionStartPrice && currentSilverPrice
    ? currentSilverPrice - sessionStartPrice
    : 0

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  return (
    <div className="fixed top-20 right-4 z-40 flex flex-col gap-2">
      {/* Live Viewer Count */}
      <motion.div
        className="bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-xl px-4 py-3 shadow-lg"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-center gap-3">
          <div className="relative">
            <Users className="w-5 h-5 text-green-400" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          </div>
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-lg font-bold text-white tabular-nums">
                {viewerCount.toLocaleString()}
              </span>
              <span className="text-xs text-gray-400">watching</span>
            </div>
            <div className="text-[10px] text-gray-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              You: {formatDuration(sessionDuration)}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Since You Arrived */}
      {sessionStartPrice && currentSilverPrice && Math.abs(priceChangeSinceArrival) > 0.01 && (
        <motion.div
          className={`bg-gray-900/95 backdrop-blur-sm border rounded-xl px-4 py-3 shadow-lg ${
            priceChangeSinceArrival >= 0
              ? 'border-green-500/30'
              : 'border-red-500/30'
          }`}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
        >
          <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
            Since you arrived
          </div>
          <div className="flex items-center gap-2">
            {priceChangeSinceArrival >= 0 ? (
              <TrendingUp className="w-4 h-4 text-green-400" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-400" />
            )}
            <span className={`text-lg font-bold ${
              priceChangeSinceArrival >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {priceChangeSinceArrival >= 0 ? '+' : ''}
              ${priceChangeSinceArrival.toFixed(2)}
            </span>
          </div>
          <div className="text-[10px] text-gray-500">
            Silver: ${sessionStartPrice.toFixed(2)} → ${currentSilverPrice.toFixed(2)}
          </div>
        </motion.div>
      )}

      {/* Recent Activity */}
      <AnimatePresence mode="popLayout">
        {recentActivity.slice(0, 1).map((activity, i) => (
          <motion.div
            key={activity + i}
            className="bg-gray-900/95 backdrop-blur-sm border border-amber-500/20 rounded-xl px-4 py-2 shadow-lg"
            initial={{ opacity: 0, x: 50, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -50, scale: 0.8 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center gap-2">
              <Zap className="w-3 h-3 text-amber-400" />
              <span className="text-xs text-gray-300">{activity}</span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

// Export a mini version for mobile
export function LiveViewerBadge() {
  const [viewerCount, setViewerCount] = useState(847)

  useEffect(() => {
    const interval = setInterval(() => {
      setViewerCount(prev => {
        const change = Math.floor(Math.random() * 10) - 4
        return Math.max(500, Math.min(2000, prev + change))
      })
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      <span className="text-gray-400">
        <span className="text-white font-medium">{viewerCount.toLocaleString()}</span> watching
      </span>
    </div>
  )
}
