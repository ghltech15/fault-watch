'use client'

import { useQuery } from '@tanstack/react-query'
import { api, CrisisGaugeData, CrackIndicator, ExposureLoss, CrisisPhase } from '@/lib/api'
import { motion } from 'framer-motion'
import { AlertTriangle, ExternalLink, CheckCircle, XCircle, Clock, Zap, Shield } from 'lucide-react'

const CRISIS_COLORS = {
  clear: '#00ff88',
  watching: '#ffd700',
  warning: '#ffaa00',
  critical: '#ff0040',
  unknown: '#666666',
}

const PHASE_COLORS = ['#00ff88', '#ffd700', '#ffaa00', '#ff3366', '#ff0040']

function StatusBadge({ status }: { status: string }) {
  const color = CRISIS_COLORS[status as keyof typeof CRISIS_COLORS] || '#666'
  const isCritical = status === 'critical'
  const isWarning = status === 'warning'

  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase border ${isCritical ? 'animate-pulse' : ''}`}
      style={{
        backgroundColor: `${color}20`,
        color: color,
        borderColor: `${color}50`,
      }}
    >
      {status}
    </span>
  )
}

function CrisisGaugeRing({ level, color }: { level: number; color: string }) {
  const size = 180
  const r = 75
  const circ = 2 * Math.PI * r
  const pct = (level / 4) * 100
  const offset = circ - (pct / 100) * circ * 0.75

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-[135deg]">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#2d2d44"
          strokeWidth={10}
          strokeDasharray={`${circ * 0.75} ${circ}`}
          strokeLinecap="round"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeDasharray={circ * 0.75}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: 'all 0.5s',
            filter: level >= 3 ? `drop-shadow(0 0 8px ${color})` : 'none',
          }}
        />
      </svg>
    </div>
  )
}

function IndicatorRow({ indicator }: { indicator: CrackIndicator }) {
  const color = CRISIS_COLORS[indicator.status as keyof typeof CRISIS_COLORS] || '#666'
  const isCritical = indicator.status === 'critical' || indicator.status === 'warning'

  return (
    <div className="flex items-center justify-between py-3 px-4 border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white">{indicator.name}</span>
          {isCritical && <AlertTriangle className="w-4 h-4 text-warning animate-pulse" />}
        </div>
        <div className="text-xs text-gray-500">{indicator.description}</div>
      </div>
      <div className="px-4 text-right">
        <div className="text-lg font-mono font-semibold" style={{ color }}>
          {indicator.value || 'N/A'}
        </div>
        {indicator.threshold && <div className="text-xs text-gray-600">Threshold: {indicator.threshold}</div>}
      </div>
      <div className="flex items-center gap-3">
        <StatusBadge status={indicator.status} />
        {indicator.source_url && (
          <a href={indicator.source_url} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-cyan-400">
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  )
}

function TierPanel({ title, subtitle, indicators, tierNum }: { title: string; subtitle: string; indicators: CrackIndicator[]; tierNum: number }) {
  const critCount = indicators.filter((i) => i.status === 'critical').length
  const warnCount = indicators.filter((i) => i.status === 'warning').length
  const hasCritical = critCount > 0
  const hasWarning = warnCount > 0

  const icons = { 1: <Zap className="w-5 h-5" />, 2: <AlertTriangle className="w-5 h-5" />, 3: <Shield className="w-5 h-5" /> }

  return (
    <div className={`bg-gray-900/80 backdrop-blur border rounded-lg ${hasCritical ? 'border-red-500/50' : hasWarning ? 'border-yellow-500/50' : 'border-gray-700/50'}`}>
      <div className="px-4 py-3 border-b border-gray-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${hasCritical ? 'bg-red-500/20 text-red-400' : hasWarning ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700/50 text-gray-400'}`}>
            {icons[tierNum as keyof typeof icons]}
          </div>
          <div>
            <h3 className="font-semibold text-white">{title}</h3>
            <p className="text-xs text-gray-500">{subtitle}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {critCount > 0 && <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse">{critCount} CRITICAL</span>}
          {warnCount > 0 && <span className="px-3 py-1 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/50">{warnCount} WARNING</span>}
        </div>
      </div>
      <div>
        {indicators.map((ind) => (
          <IndicatorRow key={ind.id} indicator={ind} />
        ))}
      </div>
    </div>
  )
}

function PhaseTracker({ phases, currentPhase }: { phases: CrisisPhase[]; currentPhase: number }) {
  return (
    <div className="space-y-3">
      {phases.map((phase) => {
        const isActive = phase.phase === currentPhase
        const isPast = phase.phase < currentPhase
        const confirmedCount = phase.indicators.filter((i) => i.status).length

        return (
          <div key={phase.phase} className={`p-3 rounded-lg border ${isActive ? 'border-yellow-500/50 bg-yellow-500/10' : isPast ? 'border-green-500/30 bg-green-500/5' : 'border-gray-700/50 bg-gray-800/30'}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isActive ? 'bg-yellow-500 text-black' : isPast ? 'bg-green-500 text-black' : 'bg-gray-700 text-gray-400'}`}>
                  {phase.phase}
                </span>
                <span className={`font-semibold ${isActive ? 'text-yellow-400' : isPast ? 'text-green-400' : 'text-gray-400'}`}>{phase.name}</span>
              </div>
              <span className="text-xs text-gray-500">
                {confirmedCount}/{phase.indicators.length} confirmed
              </span>
            </div>
            <p className="text-xs text-gray-500 mb-2">{phase.description}</p>
            <div className="flex flex-wrap gap-1">
              {phase.indicators.map((ind) => (
                <span key={ind.id} className={`text-xs px-2 py-0.5 rounded ${ind.status ? 'bg-green-500/20 text-green-400' : 'bg-gray-700/50 text-gray-500'}`}>
                  {ind.status ? '✓' : '○'} {ind.description.slice(0, 30)}...
                </span>
              ))}
            </div>
            {/* Progress bar */}
            <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
              <div className={`h-full ${isActive ? 'bg-yellow-500' : isPast ? 'bg-green-500' : 'bg-gray-600'}`} style={{ width: `${phase.progress_pct}%` }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ExposureTable({ losses, silverPrice, silverMove }: { losses: ExposureLoss[]; silverPrice: number; silverMove: number }) {
  return (
    <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700/50 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">Bank Exposure Analysis</h3>
          <p className="text-xs text-gray-500">Estimated losses at ${silverPrice.toFixed(2)}/oz (from $30 base)</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500">Silver Move</div>
          <div className="text-xl font-mono font-bold text-red-400">+${silverMove.toFixed(2)}/oz</div>
        </div>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700/50 text-xs text-gray-500 uppercase">
            <th className="px-4 py-2 text-left">Entity</th>
            <th className="px-4 py-2 text-right">Exposure</th>
            <th className="px-4 py-2 text-right">Est. Loss</th>
            <th className="px-4 py-2 text-right">vs Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {losses.map((loss) => {
            const isCritical = loss.loss_vs_cap_pct && loss.loss_vs_cap_pct > 100
            const isWarning = loss.loss_vs_cap_pct && loss.loss_vs_cap_pct > 50

            return (
              <tr key={loss.entity} className={`border-b border-gray-800/50 ${isCritical ? 'bg-red-500/10' : ''}`}>
                <td className="px-4 py-3">
                  <div className="font-medium text-white">{loss.entity}</div>
                  {!loss.is_verified && <div className="text-xs text-yellow-500">Unverified</div>}
                </td>
                <td className="px-4 py-3 text-right font-mono text-gray-300">{loss.exposure_label}</td>
                <td className={`px-4 py-3 text-right font-mono font-bold ${isCritical ? 'text-red-400' : isWarning ? 'text-yellow-400' : 'text-gray-300'}`}>{loss.loss_label}</td>
                <td className={`px-4 py-3 text-right font-mono ${isCritical ? 'text-red-400' : isWarning ? 'text-yellow-400' : 'text-gray-400'}`}>
                  {loss.loss_vs_cap_pct ? `${loss.loss_vs_cap_pct.toFixed(1)}%` : 'N/A'}
                  {isCritical && <span className="ml-1 text-red-400 animate-pulse">!</span>}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <div className="px-4 py-2 bg-gray-800/50 text-xs text-gray-500">
        <strong className="text-yellow-400">Disclaimer:</strong> Bank positions are unverified rumors. Not financial advice.
      </div>
    </div>
  )
}

// Main Card Component for Dashboard
export function CrisisGaugeCard() {
  const { data: crisis } = useQuery({ queryKey: ['crisis-gauge'], queryFn: api.getCrisisGauge, refetchInterval: 60000 })

  if (!crisis) return null

  const phaseLevel = crisis.current_phase
  const phases = ['NORMAL', 'HIDDEN STRESS', 'MARKET STRESS', 'LIQUIDITY CRISIS', 'PUBLIC CRISIS']
  const timelines = ['Months away', 'Weeks to months', 'Days to weeks', 'Hours to days', 'IMMINENT']

  return (
    <motion.div className="card cursor-pointer" whileHover={{ scale: 1.02 }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5" style={{ color: crisis.crisis_color }} />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Crisis Gauge</h3>
        <span className="ml-auto px-2 py-0.5 rounded-full text-xs font-bold" style={{ backgroundColor: `${crisis.crisis_color}20`, color: crisis.crisis_color }}>
          PHASE {phaseLevel}
        </span>
      </div>

      <div className="flex items-center justify-center mb-4">
        <div className="relative">
          <CrisisGaugeRing level={phaseLevel} color={crisis.crisis_color} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold" style={{ color: crisis.crisis_color }}>
              {crisis.crisis_level.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">CRISIS LEVEL</span>
          </div>
        </div>
      </div>

      <div className="text-center mb-4">
        <div className="text-xs text-gray-500 uppercase mb-1">Timeline Estimate</div>
        <div className="font-mono font-semibold" style={{ color: crisis.crisis_color }}>
          {timelines[phaseLevel]}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="bg-gray-800/50 rounded p-2">
          <div className="text-xs text-gray-500">Cracks Showing</div>
          <div className="font-semibold text-warning">
            {crisis.cracks_showing_count}/{crisis.total_cracks}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-2">
          <div className="text-xs text-gray-500">Silver Move</div>
          <div className="font-semibold text-danger">+${crisis.silver_move.toFixed(0)}/oz</div>
        </div>
      </div>
    </motion.div>
  )
}

// Detail View for Modal
export function CrisisGaugeDetailView() {
  const { data: crisis } = useQuery({ queryKey: ['crisis-gauge'], queryFn: api.getCrisisGauge, refetchInterval: 60000 })

  if (!crisis) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xs text-gray-500 uppercase mb-1">Silver Price</div>
          <div className="text-2xl font-mono font-bold text-white">${crisis.silver_price.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xs text-gray-500 uppercase mb-1">Current Phase</div>
          <div className="text-2xl font-bold" style={{ color: crisis.crisis_color }}>
            {crisis.current_phase}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xs text-gray-500 uppercase mb-1">Cracks Showing</div>
          <div className="text-2xl font-mono font-bold text-warning">
            {crisis.cracks_showing_count}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xs text-gray-500 uppercase mb-1">Crisis Level</div>
          <div className="text-lg font-bold" style={{ color: crisis.crisis_color }}>
            {crisis.crisis_level}
          </div>
        </div>
      </div>

      {/* Exposure Table */}
      <ExposureTable losses={crisis.losses} silverPrice={crisis.silver_price} silverMove={crisis.silver_move} />

      {/* Tier Indicators */}
      <div className="space-y-4">
        <TierPanel title="TIER 1: Immediate Warning Signs" subtitle="Check daily - highest priority" indicators={crisis.tier1_cracks} tierNum={1} />
        <TierPanel title="TIER 2: Confirming Signals" subtitle="Check weekly - validates Tier 1" indicators={crisis.tier2_cracks} tierNum={2} />
        <TierPanel title="TIER 3: Pre-Crisis Indicators" subtitle="Watch news - signals imminent crisis" indicators={crisis.tier3_cracks} tierNum={3} />
      </div>

      {/* Phase Tracker */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-lg p-4">
        <h3 className="font-semibold text-white mb-4">Crisis Phase Progression</h3>
        <PhaseTracker phases={crisis.phases} currentPhase={crisis.current_phase} />
      </div>

      {/* Resources */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-700/50 rounded-lg p-4">
        <h3 className="font-semibold text-white mb-3">Real-Time Resources</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {crisis.resources.map((resource) => (
            <a key={resource.name} href={resource.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors">
              <div>
                <div className="text-sm text-white">{resource.name}</div>
                <div className="text-xs text-gray-500">{resource.tracks}</div>
              </div>
              <ExternalLink className="w-4 h-4 text-gray-500" />
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
