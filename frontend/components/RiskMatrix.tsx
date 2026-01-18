'use client'

import { useQuery } from '@tanstack/react-query'
import { api, RiskMatrixData, RiskFactor, MonitoringPeriod, MonitorItem, ImmediatePriority } from '@/lib/api'
import { Grid3X3, TrendingUp, TrendingDown, Minus, Clock, Search, AlertTriangle, ChevronRight, Calendar, Eye, Copy, Check, Target, Gauge } from 'lucide-react'
import { useState } from 'react'

// Risk level colors
const getRiskColor = (level: string): { bg: string; text: string } => {
  const l = level.toLowerCase()
  if (l.includes('higher') || l.includes('high')) return { bg: 'bg-red-900/30', text: 'text-red-400' }
  if (l.includes('rising')) return { bg: 'bg-orange-900/30', text: 'text-orange-400' }
  if (l.includes('medium-high')) return { bg: 'bg-orange-900/30', text: 'text-orange-400' }
  if (l.includes('medium') || l.includes('moderate')) return { bg: 'bg-yellow-900/30', text: 'text-yellow-400' }
  if (l.includes('elevated')) return { bg: 'bg-yellow-900/30', text: 'text-yellow-400' }
  if (l.includes('low-medium')) return { bg: 'bg-blue-900/30', text: 'text-blue-400' }
  if (l.includes('low')) return { bg: 'bg-green-900/30', text: 'text-green-400' }
  return { bg: 'bg-gray-900/30', text: 'text-gray-400' }
}

// Direction icon
function DirectionIcon({ direction }: { direction: string }) {
  if (direction === 'up') return <TrendingUp className="w-4 h-4 text-red-400" />
  if (direction === 'down') return <TrendingDown className="w-4 h-4 text-green-400" />
  return <Minus className="w-4 h-4 text-gray-400" />
}

// Risk Factor Row
function RiskFactorRow({ factor }: { factor: RiskFactor }) {
  const preColors = getRiskColor(factor.pre_greenland)
  const postColors = getRiskColor(factor.post_greenland)

  return (
    <div className="grid grid-cols-12 gap-2 py-2 border-b border-gray-700/50 items-center">
      <div className="col-span-4 text-sm text-gray-300">{factor.name}</div>
      <div className={`col-span-3 text-center py-1 rounded text-xs font-medium ${preColors.bg} ${preColors.text}`}>
        {factor.pre_greenland}
      </div>
      <div className="col-span-1 flex justify-center">
        <DirectionIcon direction={factor.change_direction} />
      </div>
      <div className={`col-span-4 text-center py-1 rounded text-xs font-bold ${postColors.bg} ${postColors.text}`}>
        {factor.post_greenland}
      </div>
    </div>
  )
}

// Monitor Item
function MonitorItemRow({ item }: { item: MonitorItem }) {
  return (
    <div className={`flex items-center gap-2 text-sm py-1 ${item.priority === 'high' ? 'text-orange-400' : 'text-gray-400'}`}>
      {item.priority === 'high' ? (
        <AlertTriangle className="w-3 h-3" />
      ) : (
        <ChevronRight className="w-3 h-3" />
      )}
      {item.item}
    </div>
  )
}

// Monitoring Period Section
function MonitoringSection({ period }: { period: MonitoringPeriod }) {
  const periodColors: Record<string, string> = {
    'Sunday Night': 'text-purple-400 border-purple-500/30',
    'Monday-Tuesday': 'text-blue-400 border-blue-500/30',
    'Later This Week': 'text-cyan-400 border-cyan-500/30',
  }
  const colors = periodColors[period.period] || 'text-gray-400 border-gray-500/30'

  return (
    <div className={`p-3 rounded-lg border bg-gray-800/30 ${colors.split(' ')[1]}`}>
      <div className={`font-semibold mb-2 flex items-center gap-2 ${colors.split(' ')[0]}`}>
        <Clock className="w-4 h-4" />
        {period.period}
      </div>
      <div className="space-y-1">
        {period.items.map((item, i) => (
          <MonitorItemRow key={i} item={item} />
        ))}
      </div>
    </div>
  )
}

// Search Query with copy button
function SearchQuery({ query }: { query: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(query)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className="flex items-center justify-between gap-2 px-2 py-1 bg-gray-800/50 rounded text-xs font-mono text-gray-400 hover:bg-gray-700/50 cursor-pointer group"
      onClick={handleCopy}
    >
      <span className="truncate">{query}</span>
      {copied ? (
        <Check className="w-3 h-3 text-green-400 flex-shrink-0" />
      ) : (
        <Copy className="w-3 h-3 text-gray-600 group-hover:text-gray-400 flex-shrink-0" />
      )}
    </div>
  )
}

// Immediate Priority Row
function ImmediatePriorityRow({ priority }: { priority: ImmediatePriority }) {
  return (
    <div className="p-3 rounded-lg bg-gray-800/50 border border-red-500/20 hover:border-red-500/40 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="font-semibold text-white">{priority.name}</span>
        </div>
        <span className="text-xs px-2 py-0.5 bg-red-900/30 text-red-400 rounded font-mono">
          {priority.threshold}
        </span>
      </div>
      <div className="text-xs text-gray-400 mb-2">{priority.metric}</div>
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1">
          <Gauge className="w-3 h-3 text-blue-400" />
          <span className="text-blue-400">{priority.current_status}</span>
        </div>
      </div>
      <div className="mt-2 text-xs text-orange-300/80 italic">
        {priority.signal_meaning}
      </div>
    </div>
  )
}

// Main card for dashboard
export function RiskMatrixCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['risk-matrix'],
    queryFn: api.getRiskMatrix,
    refetchInterval: 300000, // 5 minutes
  })

  if (isLoading || !data) {
    return (
      <div className="card cursor-pointer hover:border-purple-500/50 transition-colors">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-32 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  // Count factors that increased risk
  const increasedRisks = data.risk_factors.filter(f => f.change_direction === 'up').length
  const highPriorityItems = data.monitoring_schedule.flatMap(p => p.items).filter(i => i.priority === 'high').length

  return (
    <div className="card cursor-pointer hover:border-purple-500/50 transition-colors border border-purple-500/20">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Grid3X3 className="w-5 h-5 text-purple-400" />
          <h3 className="font-bold text-white">Risk Matrix</h3>
        </div>
        <span className="text-xs text-gray-500">{data.last_updated}</span>
      </div>

      {/* Context Event Banner */}
      <div className="bg-purple-900/20 text-purple-400 px-3 py-2 rounded-lg mb-3 text-sm">
        <div className="font-bold">{data.context_event}</div>
        <div className="text-xs text-purple-300/70 mt-1 line-clamp-2">{data.context_description}</div>
      </div>

      {/* Risk Summary */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center p-2 bg-red-900/20 rounded">
          <TrendingUp className="w-4 h-4 mx-auto mb-1 text-red-400" />
          <div className="text-lg font-bold text-red-400">{increasedRisks}/{data.risk_factors.length}</div>
          <div className="text-[10px] text-gray-400">Risks Up</div>
        </div>
        <div className="text-center p-2 bg-orange-900/20 rounded">
          <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-orange-400" />
          <div className="text-lg font-bold text-orange-400">{highPriorityItems}</div>
          <div className="text-[10px] text-gray-400">High Priority</div>
        </div>
        <div className="text-center p-2 bg-purple-900/20 rounded">
          <Target className="w-4 h-4 mx-auto mb-1 text-purple-400" />
          <div className="text-lg font-bold text-purple-400">{data.immediate_priorities?.length || 0}</div>
          <div className="text-[10px] text-gray-400">Immediate</div>
        </div>
      </div>

      {/* Mini Matrix Preview */}
      <div className="space-y-1 mb-3">
        {data.risk_factors.slice(0, 3).map((factor, i) => {
          const postColors = getRiskColor(factor.post_greenland)
          return (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-gray-400 truncate flex-1">{factor.name}</span>
              <DirectionIcon direction={factor.change_direction} />
              <span className={`ml-2 px-2 py-0.5 rounded ${postColors.bg} ${postColors.text}`}>
                {factor.post_greenland}
              </span>
            </div>
          )
        })}
      </div>

      <div className="text-xs text-gray-500">
        {data.monitoring_schedule.length} monitoring periods | {data.search_queries.length} search queries
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 flex items-center gap-1">
        <ChevronRight className="w-3 h-3" />
        Click for full matrix, monitoring schedule & queries
      </div>
    </div>
  )
}

// Detail view for modal
export function RiskMatrixDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['risk-matrix'],
    queryFn: api.getRiskMatrix,
  })

  if (isLoading || !data) {
    return <div className="text-gray-400">Loading risk matrix data...</div>
  }

  return (
    <div className="space-y-6">
      {/* Context Banner */}
      <div className="p-4 rounded-lg bg-purple-900/20 border border-purple-500/30">
        <div className="flex items-center gap-2 mb-2">
          <Grid3X3 className="w-6 h-6 text-purple-400" />
          <span className="text-xl font-bold text-purple-400">{data.context_event}</span>
        </div>
        <p className="text-gray-300">{data.context_description}</p>
        <div className="mt-3 text-xs text-gray-500">Last Updated: {data.last_updated}</div>
      </div>

      {/* Risk Matrix Table */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <TrendingUp className="w-5 h-5 text-red-400" /> Risk Factor Comparison
        </h4>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          {/* Header */}
          <div className="grid grid-cols-12 gap-2 pb-2 border-b border-gray-600 mb-2">
            <div className="col-span-4 text-xs text-gray-500 font-semibold">FACTOR</div>
            <div className="col-span-3 text-xs text-gray-500 font-semibold text-center">PRE-GREENLAND</div>
            <div className="col-span-1"></div>
            <div className="col-span-4 text-xs text-gray-500 font-semibold text-center">POST-GREENLAND</div>
          </div>
          {/* Rows */}
          {data.risk_factors.map((factor, i) => (
            <RiskFactorRow key={i} factor={factor} />
          ))}
        </div>
      </div>

      {/* Bottom Line */}
      <div className="p-4 bg-orange-900/20 rounded-lg border border-orange-500/30">
        <h5 className="font-bold text-orange-400 mb-2 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" /> Bottom Line
        </h5>
        <p className="text-gray-300">{data.bottom_line}</p>
      </div>

      {/* Immediate Monitoring Priorities */}
      {data.immediate_priorities && data.immediate_priorities.length > 0 && (
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
            <Target className="w-5 h-5 text-red-400" /> Immediate Monitoring Priorities
          </h4>
          <p className="text-sm text-gray-400 mb-3">Critical indicators to watch for early warning signals</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {data.immediate_priorities.map((priority, i) => (
              <ImmediatePriorityRow key={i} priority={priority} />
            ))}
          </div>
        </div>
      )}

      {/* What to Monitor */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Eye className="w-5 h-5 text-blue-400" /> What to Monitor This Week
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.monitoring_schedule.map((period, i) => (
            <MonitoringSection key={i} period={period} />
          ))}
        </div>
      </div>

      {/* Search Queries */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Search className="w-5 h-5 text-cyan-400" /> Search Queries
        </h4>
        <p className="text-sm text-gray-400 mb-3">Click any query to copy to clipboard</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
          {data.search_queries.map((query, i) => (
            <SearchQuery key={i} query={query} />
          ))}
        </div>
      </div>
    </div>
  )
}
