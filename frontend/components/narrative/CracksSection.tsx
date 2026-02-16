'use client'

import { motion } from 'framer-motion'
import { Activity, CheckCircle, AlertTriangle, XCircle, Eye, Coins, Building2, CreditCard, Car, Home, Landmark } from 'lucide-react'
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

// Sector definitions with their indicators
interface SectorDefinition {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  indicatorNames: string[] // Maps to indicator names from props
  placeholder?: boolean // True if no real data yet
}

const SECTORS: SectorDefinition[] = [
  {
    id: 'silver',
    name: 'Silver & Precious Metals',
    icon: <Coins className="w-5 h-5" />,
    color: 'cyan',
    indicatorNames: ['COMEX Delivery Failures', 'Gold-Silver Ratio', 'ETF Outflows', 'Dealer Positioning']
  },
  {
    id: 'banks',
    name: 'Banks / Funding Markets',
    icon: <Building2 className="w-5 h-5" />,
    color: 'red',
    indicatorNames: ['Credit Default Swaps', 'Bank Stock Volatility', 'Interbank Lending', 'LBMA Forward Rates']
  },
  {
    id: 'consumer',
    name: 'Consumer Credit',
    icon: <CreditCard className="w-5 h-5" />,
    color: 'amber',
    indicatorNames: [],
    placeholder: true
  },
  {
    id: 'auto',
    name: 'Auto Loans',
    icon: <Car className="w-5 h-5" />,
    color: 'orange',
    indicatorNames: [],
    placeholder: true
  },
  {
    id: 'housing',
    name: 'Housing / Foreclosures',
    icon: <Home className="w-5 h-5" />,
    color: 'purple',
    indicatorNames: [],
    placeholder: true
  },
  {
    id: 'govt',
    name: 'Government / Central Bank',
    icon: <Landmark className="w-5 h-5" />,
    color: 'blue',
    indicatorNames: ['Fed Facility Usage', 'Dollar Liquidity', 'Repo Market Stress', 'Treasury Volatility']
  }
]

// Determine sector status from its indicators
function getSectorStatus(indicators: CrackIndicator[]): 'stable' | 'elevated' | 'stressed' | 'breaking' {
  const breakingCount = indicators.filter(i => i.status === 'breaking').length
  const stressedCount = indicators.filter(i => i.status === 'stressed').length

  if (breakingCount > 0) return 'breaking'
  if (stressedCount >= 2) return 'stressed'
  if (stressedCount === 1) return 'elevated'
  return 'stable'
}

// Generate interpretive sentence for sector
function getSectorSentence(sectorId: string, status: string, indicators: CrackIndicator[]): string {
  if (indicators.length === 0) {
    return 'Data coming soon. We are adding new indicators to this sector.'
  }

  const stressedIndicators = indicators.filter(i => i.status !== 'stable')

  switch (sectorId) {
    case 'silver':
      if (status === 'breaking') return 'Physical silver markets showing severe strain with delivery failures.'
      if (status === 'stressed') return 'COMEX and dealer markets under pressure; physical premiums likely rising.'
      if (status === 'elevated') return 'Minor stress signals in precious metals markets.'
      return 'Silver markets functioning normally with adequate supply.'

    case 'banks':
      if (status === 'breaking') return 'Banking sector in distress; credit markets freezing.'
      if (status === 'stressed') return 'Banks showing stress; CDS spreads and volatility elevated.'
      if (status === 'elevated') return 'Early warning signs in bank funding markets.'
      return 'Banking sector stable with normal credit conditions.'

    case 'govt':
      if (status === 'breaking') return 'Emergency Fed facilities activated; crisis response underway.'
      if (status === 'stressed') return 'Unusual activity in Fed facilities and Treasury markets.'
      if (status === 'elevated') return 'Government watchdogs on alert; monitoring increased.'
      return 'No unusual central bank or government activity detected.'

    default:
      return 'Monitoring this sector for early warning signs.'
  }
}

const statusConfig = {
  stable: { label: 'Stable', color: 'green', bgClass: 'bg-green-500/10 border-green-500/30' },
  elevated: { label: 'Elevated', color: 'yellow', bgClass: 'bg-yellow-500/10 border-yellow-500/30' },
  stressed: { label: 'Stressed', color: 'amber', bgClass: 'bg-amber-500/10 border-amber-500/30' },
  breaking: { label: 'Breaking', color: 'red', bgClass: 'bg-red-500/10 border-red-500/30 animate-pulse' }
}

const colorMap: Record<string, string> = {
  cyan: 'text-cyan-400',
  red: 'text-red-400',
  amber: 'text-amber-400',
  orange: 'text-orange-400',
  purple: 'text-purple-400',
  blue: 'text-blue-400'
}

const bgColorMap: Record<string, string> = {
  cyan: 'bg-cyan-500/20',
  red: 'bg-red-500/20',
  amber: 'bg-amber-500/20',
  orange: 'bg-orange-500/20',
  purple: 'bg-purple-500/20',
  blue: 'bg-blue-500/20'
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

  return (
    <NarrativeSection
      id="cracks"
      phaseNumber={3}
      title="THE CRACKS"
      subtitle="Early warning signs of systemic stress across key sectors. When multiple sectors turn red, the cascade may be beginning."
      status={status}
      flowText="Bank losses trigger credit stress and early warning signals"
    >
      {/* Status Summary */}
      <div className="grid grid-cols-4 gap-3 mb-8">
        {(['stable', 'elevated', 'stressed', 'breaking'] as const).map((s) => {
          const sectorStatuses = SECTORS.map(sector => {
            const sectorIndicators = indicators.filter(i =>
              sector.indicatorNames.includes(i.name)
            )
            return getSectorStatus(sectorIndicators)
          })
          const count = sectorStatuses.filter(ss => ss === s).length

          return (
            <div
              key={s}
              className={`${statusConfig[s].bgClass} border rounded-xl p-3 text-center`}
            >
              <div className={`text-2xl font-black text-${statusConfig[s].color}-400`}>
                {count}
              </div>
              <div className={`text-xs text-${statusConfig[s].color}-400/70 uppercase tracking-wider mt-1`}>
                {statusConfig[s].label}
              </div>
            </div>
          )
        })}
      </div>

      {/* Sector Cards - 6 card grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {SECTORS.map((sector, index) => {
          // Get indicators for this sector
          const sectorIndicators = indicators.filter(i =>
            sector.indicatorNames.includes(i.name)
          )
          const sectorStatus = sector.placeholder ? 'stable' : getSectorStatus(sectorIndicators)
          const config = statusConfig[sectorStatus]

          return (
            <motion.div
              key={sector.id}
              className={`relative p-5 rounded-xl border ${config.bgClass}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${bgColorMap[sector.color]}`}>
                    <span className={colorMap[sector.color]}>{sector.icon}</span>
                  </div>
                  <h4 className="font-bold text-white text-sm">{sector.name}</h4>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold uppercase text-${config.color}-400 bg-${config.color}-500/20`}>
                  {config.label}
                </span>
              </div>

              {/* Indicators or placeholder */}
              {sector.placeholder ? (
                <div className="text-gray-500 text-sm italic py-4 text-center border-t border-gray-800">
                  Data coming soon
                </div>
              ) : (
                <div className="space-y-2 mb-3">
                  {sectorIndicators.slice(0, 4).map((indicator) => (
                    <div
                      key={indicator.name}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-gray-400 truncate">{indicator.name}</span>
                      <div className="flex items-center gap-2">
                        {indicator.currentValue && (
                          <span className="text-gray-300 font-medium">{indicator.currentValue}</span>
                        )}
                        {indicator.status === 'stable' && <CheckCircle className="w-3 h-3 text-green-400" />}
                        {indicator.status === 'stressed' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                        {indicator.status === 'breaking' && <XCircle className="w-3 h-3 text-red-400" />}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Interpretive sentence */}
              <p className="text-xs text-gray-400 pt-3 border-t border-gray-800">
                {getSectorSentence(sector.id, sectorStatus, sectorIndicators)}
              </p>
            </motion.div>
          )
        })}
      </div>

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
              These sectors are monitored continuously. When multiple sectors show &quot;Stressed&quot; or &quot;Breaking&quot;,
              it signals increasing systemic risk across the financial system.
            </p>
            <div className="mt-3 flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1 text-green-400">
                <Activity className="w-3 h-3" /> Auto-refresh: 5 min
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
  // Silver & PM
  { name: 'COMEX Delivery Failures', category: 'tier1', status: 'stressed', description: 'Physical delivery backlog', currentValue: '12 days', threshold: '30 days' },
  { name: 'Gold-Silver Ratio', category: 'tier2', status: 'stressed', description: 'Abnormal ratio movement', currentValue: '78:1', threshold: '100:1' },
  { name: 'ETF Outflows', category: 'tier2', status: 'stable', description: 'SLV/PSLV redemptions', currentValue: '-2.3M oz', threshold: '-10M oz' },
  { name: 'Dealer Positioning', category: 'tier2', status: 'stressed', description: 'COT report shorts', currentValue: '142K', threshold: '200K' },

  // Banks
  { name: 'Credit Default Swaps', category: 'tier1', status: 'stressed', description: 'Bank CDS spreads widening', currentValue: '+45 bps', threshold: '+100 bps' },
  { name: 'Bank Stock Volatility', category: 'tier1', status: 'stable', description: 'Financial sector VIX', currentValue: '24.5', threshold: '40' },
  { name: 'Interbank Lending', category: 'tier3', status: 'stable', description: 'LIBOR-OIS spread', currentValue: '12 bps', threshold: '50 bps' },
  { name: 'LBMA Forward Rates', category: 'tier2', status: 'stable', description: 'London forward curve', currentValue: 'Normal', threshold: 'Inverted' },

  // Government / CB
  { name: 'Fed Facility Usage', category: 'tier3', status: 'stable', description: 'Emergency lending', currentValue: '$0.2B', threshold: '$50B' },
  { name: 'Dollar Liquidity', category: 'tier3', status: 'stable', description: 'Global USD shortage', currentValue: 'Normal', threshold: 'Stressed' },
  { name: 'Repo Market Stress', category: 'tier1', status: 'stable', description: 'Overnight funding rates', currentValue: '5.35%', threshold: '6.0%' },
  { name: 'Treasury Volatility', category: 'tier3', status: 'stable', description: 'MOVE index', currentValue: '98', threshold: '150' }
]
