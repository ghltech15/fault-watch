'use client'

import { motion } from 'framer-motion'
import { Activity, CheckCircle, AlertTriangle, XCircle, Radio, Eye } from 'lucide-react'
import { NarrativeSection } from './NarrativeSection'

interface CrackIndicator {
  name: string
  category: 'tier1' | 'tier2' | 'tier3'
  status: 'stable' | 'stressed' | 'breaking'
  description: string
  currentValue?: string
  threshold?: string
}

interface CracksSectionProps {
  indicators: CrackIndicator[]
  cracksActive: number
  totalCracks: number
}

export function CracksSection({
  indicators = defaultIndicators,
  cracksActive,
  totalCracks
}: CracksSectionProps) {
  const breakingCount = indicators.filter(i => i.status === 'breaking').length
  const stressedCount = indicators.filter(i => i.status === 'stressed').length

  const status = breakingCount > 0 ? 'critical' :
                 stressedCount >= 3 ? 'warning' : 'active'

  const statusIcons = {
    stable: <CheckCircle className="w-4 h-4 text-green-400" />,
    stressed: <AlertTriangle className="w-4 h-4 text-amber-400" />,
    breaking: <XCircle className="w-4 h-4 text-red-400" />
  }

  const statusColors = {
    stable: 'border-green-500/30 bg-green-500/5',
    stressed: 'border-amber-500/30 bg-amber-500/5',
    breaking: 'border-red-500/30 bg-red-500/5 animate-pulse'
  }

  const tierLabels = {
    tier1: { label: 'TIER 1', color: 'text-red-400', description: 'Critical early warnings' },
    tier2: { label: 'TIER 2', color: 'text-amber-400', description: 'Secondary stress signals' },
    tier3: { label: 'TIER 3', color: 'text-blue-400', description: 'Systemic indicators' }
  }

  const groupedIndicators = {
    tier1: indicators.filter(i => i.category === 'tier1'),
    tier2: indicators.filter(i => i.category === 'tier2'),
    tier3: indicators.filter(i => i.category === 'tier3')
  }

  return (
    <NarrativeSection
      id="cracks"
      phaseNumber={3}
      title="THE CRACKS"
      subtitle="Early warning signs of systemic stress. When these indicators turn red, the cascade is beginning."
      status={status}
      flowText="Bank losses trigger credit stress and early warning signals"
    >
      {/* Status Summary */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 text-center">
          <div className="text-3xl font-black text-green-400">
            {indicators.filter(i => i.status === 'stable').length}
          </div>
          <div className="text-xs text-green-400/70 uppercase tracking-wider mt-1">Stable</div>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 text-center">
          <div className="text-3xl font-black text-amber-400">{stressedCount}</div>
          <div className="text-xs text-amber-400/70 uppercase tracking-wider mt-1">Stressed</div>
        </div>
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-center">
          <div className="text-3xl font-black text-red-400">{breakingCount}</div>
          <div className="text-xs text-red-400/70 uppercase tracking-wider mt-1">Breaking</div>
        </div>
      </div>

      {/* Indicators by Tier */}
      {(['tier1', 'tier2', 'tier3'] as const).map((tier) => (
        <div key={tier} className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-2 py-1 rounded text-xs font-bold ${tierLabels[tier].color} bg-gray-800`}>
              {tierLabels[tier].label}
            </span>
            <span className="text-sm text-gray-500">{tierLabels[tier].description}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {groupedIndicators[tier].map((indicator, index) => (
              <motion.div
                key={indicator.name}
                className={`relative p-4 rounded-xl border ${statusColors[indicator.status]}`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {statusIcons[indicator.status]}
                    <span className="font-medium text-white text-sm">{indicator.name}</span>
                  </div>
                  <span className={`text-xs font-bold uppercase ${
                    indicator.status === 'stable' ? 'text-green-400' :
                    indicator.status === 'stressed' ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {indicator.status}
                  </span>
                </div>

                <p className="text-xs text-gray-400 mb-2">{indicator.description}</p>

                {indicator.currentValue && (
                  <div className="flex items-center justify-between text-xs mt-2 pt-2 border-t border-gray-800">
                    <span className="text-gray-500">Current: <span className="text-white font-medium">{indicator.currentValue}</span></span>
                    {indicator.threshold && (
                      <span className="text-gray-500">Threshold: <span className="text-amber-400">{indicator.threshold}</span></span>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      ))}

      {/* Monitoring Alert */}
      <motion.div
        className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-500/20 rounded-lg">
            <Eye className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h4 className="font-bold text-white mb-1">24/7 Automated Monitoring</h4>
            <p className="text-gray-400 text-sm">
              These indicators are monitored in real-time. When multiple Tier 1 indicators turn "Breaking",
              it signals the beginning of a cascade event.
            </p>
            <div className="mt-3 flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1 text-green-400">
                <Radio className="w-3 h-3" /> Auto-refresh: 5 min
              </span>
              <span className="text-gray-500">
                Last scan: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </NarrativeSection>
  )
}

const defaultIndicators: CrackIndicator[] = [
  // Tier 1 - Critical
  { name: 'Credit Default Swaps', category: 'tier1', status: 'stressed', description: 'Bank CDS spreads widening', currentValue: '+45 bps', threshold: '+100 bps' },
  { name: 'Repo Market Stress', category: 'tier1', status: 'stable', description: 'Overnight funding rates', currentValue: '5.35%', threshold: '6.0%' },
  { name: 'COMEX Delivery Failures', category: 'tier1', status: 'stressed', description: 'Physical delivery backlog', currentValue: '12 days', threshold: '30 days' },
  { name: 'Bank Stock Volatility', category: 'tier1', status: 'stable', description: 'Financial sector VIX', currentValue: '24.5', threshold: '40' },

  // Tier 2 - Secondary
  { name: 'Gold-Silver Ratio', category: 'tier2', status: 'stressed', description: 'Abnormal ratio movement', currentValue: '78:1', threshold: '100:1' },
  { name: 'LBMA Forward Rates', category: 'tier2', status: 'stable', description: 'London forward curve', currentValue: 'Normal', threshold: 'Inverted' },
  { name: 'ETF Outflows', category: 'tier2', status: 'stable', description: 'SLV/PSLV redemptions', currentValue: '-2.3M oz', threshold: '-10M oz' },
  { name: 'Dealer Positioning', category: 'tier2', status: 'stressed', description: 'COT report shorts', currentValue: '142K', threshold: '200K' },

  // Tier 3 - Systemic
  { name: 'Fed Facility Usage', category: 'tier3', status: 'stable', description: 'Emergency lending', currentValue: '$0.2B', threshold: '$50B' },
  { name: 'Treasury Volatility', category: 'tier3', status: 'stable', description: 'MOVE index', currentValue: '98', threshold: '150' },
  { name: 'Dollar Liquidity', category: 'tier3', status: 'stable', description: 'Global USD shortage', currentValue: 'Normal', threshold: 'Stressed' },
  { name: 'Interbank Lending', category: 'tier3', status: 'stable', description: 'LIBOR-OIS spread', currentValue: '12 bps', threshold: '50 bps' }
]
