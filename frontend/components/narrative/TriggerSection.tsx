'use client'

import { motion } from 'framer-motion'
import { TrendingUp, Target, Zap, AlertTriangle } from 'lucide-react'
import { NarrativeSection } from './NarrativeSection'

interface PriceTarget {
  price: number
  label: string
  impact: string
  status: 'reached' | 'approaching' | 'distant'
}

interface TriggerSectionProps {
  silverPrice: number
  silverChange: number
  comexInventory: number
  targets?: PriceTarget[]
}

export function TriggerSection({
  silverPrice,
  silverChange,
  comexInventory,
  targets = defaultTargets
}: TriggerSectionProps) {
  // Determine section status based on silver price
  const status = silverPrice >= 75 ? 'critical' : silverPrice >= 50 ? 'warning' : 'active'

  return (
    <NarrativeSection
      id="trigger"
      phaseNumber={1}
      title="THE TRIGGER"
      subtitle="Silver price movement is the catalyst that drives bank losses. Every dollar increase compounds short position exposure exponentially."
      status={status}
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Main Silver Price Display */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8 relative overflow-hidden">
          {/* Background glow */}
          <div
            className="absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-20"
            style={{
              background: silverChange >= 0 ? 'rgb(34,197,94)' : 'rgb(239,68,68)'
            }}
          />

          <div className="relative">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-400 uppercase tracking-wider font-medium">Silver Spot Price</span>
            </div>

            <div className="flex items-baseline gap-4 mb-4">
              <span className="text-6xl md:text-7xl font-black text-white tabular-nums">
                ${silverPrice.toFixed(2)}
              </span>
              <span
                className={`text-2xl font-bold flex items-center gap-1 ${
                  silverChange >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                <TrendingUp className={`w-6 h-6 ${silverChange < 0 ? 'rotate-180' : ''}`} />
                {silverChange >= 0 ? '+' : ''}{silverChange.toFixed(2)}%
              </span>
            </div>

            <p className="text-gray-500 text-sm">
              Per ounce • COMEX/LBMA spot
            </p>

            {/* Mini progress to $50 */}
            <div className="mt-6">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-gray-500">Progress to $50 trigger</span>
                <span className="text-amber-400 font-bold">{((silverPrice / 50) * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-amber-500 to-red-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min((silverPrice / 50) * 100, 100)}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Price Targets */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Price Targets & Impact
          </h3>

          {targets.map((target, index) => {
            const isReached = silverPrice >= target.price
            const isNext = !isReached && (index === 0 || silverPrice >= targets[index - 1].price)

            return (
              <motion.div
                key={target.price}
                className={`relative p-4 rounded-xl border transition-all ${
                  isReached
                    ? 'bg-green-500/10 border-green-500/30'
                    : isNext
                    ? 'bg-amber-500/10 border-amber-500/30'
                    : 'bg-gray-900/50 border-gray-800'
                }`}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl font-black ${isReached ? 'text-green-400' : isNext ? 'text-amber-400' : 'text-gray-400'}`}>
                      ${target.price}
                    </span>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${
                      isReached
                        ? 'bg-green-500/20 text-green-400'
                        : isNext
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-gray-800 text-gray-500'
                    }`}>
                      {target.label}
                    </span>
                  </div>
                  {isReached && (
                    <span className="text-green-400 text-xs font-bold">REACHED</span>
                  )}
                  {isNext && (
                    <span className="text-amber-400 text-xs font-bold animate-pulse">NEXT TARGET</span>
                  )}
                </div>
                <p className="text-sm text-gray-400">{target.impact}</p>

                {/* Progress indicator for next target */}
                {isNext && (
                  <div className="mt-3">
                    <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-amber-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${((silverPrice - (targets[index - 1]?.price || 0)) / (target.price - (targets[index - 1]?.price || 0))) * 100}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* COMEX Inventory Alert */}
      <motion.div
        className="mt-8 bg-red-500/10 border border-red-500/30 rounded-xl p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-red-500/20 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <h4 className="font-bold text-white mb-1">COMEX Registered Inventory Depleting</h4>
            <p className="text-gray-400 text-sm mb-2">
              Physical silver available for delivery: <span className="text-red-400 font-bold">{(comexInventory / 1000000).toFixed(1)}M oz</span>
            </p>
            <p className="text-gray-500 text-xs">
              At current delivery rates, inventory could be depleted within 6-12 months. This creates delivery pressure and exposes paper short positions.
            </p>
          </div>
        </div>
      </motion.div>
    </NarrativeSection>
  )
}

const defaultTargets: PriceTarget[] = [
  {
    price: 50,
    label: 'CRISIS',
    impact: 'All-time high breached. Margin calls triggered forced covering.',
    status: 'reached'
  },
  {
    price: 75,
    label: 'CRITICAL',
    impact: 'Major bank losses materialized. Credit stress spreading to other markets.',
    status: 'reached'
  },
  {
    price: 100,
    label: 'SYSTEMIC',
    impact: 'Potential bank insolvencies. Government intervention likely.',
    status: 'approaching'
  },
  {
    price: 150,
    label: 'COLLAPSE',
    impact: 'Multiple bank failures. Credit markets frozen. Fed emergency intervention.',
    status: 'distant'
  }
]
