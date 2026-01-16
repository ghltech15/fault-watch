'use client'

import { useQuery } from '@tanstack/react-query'
import { api, GovernmentInterventionData, ControlLevel, EquityStake, ChokepointAsset, RegulatoryAction, DPAAction, StrategicScenario } from '@/lib/api'
import { AlertTriangle, Shield, Building2, Truck, FileText, Target, ChevronRight, Lock, Globe, Factory, Scale } from 'lucide-react'

// Control level colors
const controlColors: Record<ControlLevel, { bg: string; text: string; border: string }> = {
  low: { bg: 'bg-green-900/20', text: 'text-green-400', border: 'border-green-500/30' },
  medium: { bg: 'bg-yellow-900/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  high: { bg: 'bg-orange-900/20', text: 'text-orange-400', border: 'border-orange-500/30' },
  confirmed: { bg: 'bg-red-900/20', text: 'text-red-400', border: 'border-red-500/30' },
}

// Control level badge
function ControlBadge({ level }: { level: ControlLevel }) {
  const colors = controlColors[level]
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
      {level.toUpperCase()}
    </span>
  )
}

// Main card for dashboard
export function GovernmentInterventionCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['government-intervention'],
    queryFn: api.getGovernmentIntervention,
    refetchInterval: 120000, // 2 minutes
  })

  if (isLoading || !data) {
    return (
      <div className="card cursor-pointer hover:border-purple-500/50 transition-colors">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  const colors = controlColors[data.overall_control_level]

  return (
    <div className={`card cursor-pointer hover:border-purple-500/50 transition-colors ${colors.border} border`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-purple-400" />
          <h3 className="font-bold text-white">Administrative Control</h3>
        </div>
        <ControlBadge level={data.overall_control_level} />
      </div>

      {data.administrative_override_active && (
        <div className={`${colors.bg} ${colors.text} px-3 py-2 rounded-lg mb-3 text-sm flex items-center gap-2`}>
          <Lock className="w-4 h-4" />
          <span className="font-medium">Override Active</span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="text-center p-2 bg-gray-800/50 rounded">
          <div className="text-2xl font-bold text-purple-400">{data.equity_stakes.length}</div>
          <div className="text-xs text-gray-400">Govt Stakes</div>
        </div>
        <div className="text-center p-2 bg-gray-800/50 rounded">
          <div className="text-2xl font-bold text-orange-400">{data.chokepoints.length}</div>
          <div className="text-xs text-gray-400">Chokepoints</div>
        </div>
        <div className="text-center p-2 bg-gray-800/50 rounded">
          <div className="text-2xl font-bold text-yellow-400">{data.regulatory_actions.length}</div>
          <div className="text-xs text-gray-400">Reg Actions</div>
        </div>
        <div className="text-center p-2 bg-gray-800/50 rounded">
          <div className="text-2xl font-bold text-red-400">{data.dpa_actions.length}</div>
          <div className="text-xs text-gray-400">DPA Signals</div>
        </div>
      </div>

      <div className="text-sm">
        <div className="flex items-center gap-2 text-gray-400">
          <Target className="w-4 h-4 text-yellow-500" />
          <span>Current: <span className="text-white font-medium">{data.current_scenario}</span></span>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 flex items-center gap-1">
        <ChevronRight className="w-3 h-3" />
        Click for strategic intervention analysis
      </div>
    </div>
  )
}

// Detail view for modal
export function GovernmentInterventionDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['government-intervention'],
    queryFn: api.getGovernmentIntervention,
  })

  if (isLoading || !data) {
    return <div className="text-gray-400">Loading intervention data...</div>
  }

  return (
    <div className="space-y-6">
      {/* Alert Banner */}
      {data.alert_message && (
        <div className={`${controlColors[data.overall_control_level].bg} p-4 rounded-lg border ${controlColors[data.overall_control_level].border}`}>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className={`w-5 h-5 ${controlColors[data.overall_control_level].text}`} />
            <span className={`font-bold ${controlColors[data.overall_control_level].text}`}>Administrative Override Detected</span>
          </div>
          <p className="text-gray-300 text-sm">{data.alert_message}</p>
        </div>
      )}

      {/* Signal Hierarchy */}
      <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-purple-400">
          <Scale className="w-4 h-4" /> Signal Interpretation Rules
        </h4>
        <div className="space-y-1 text-sm">
          {Object.entries(data.signal_hierarchy).filter(([k]) => k.startsWith('rule')).map(([key, value]) => (
            <div key={key} className="flex items-start gap-2 text-gray-300">
              <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
              <span>{value}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 pt-3 border-t border-purple-500/30 text-xs text-purple-300">
          {data.signal_hierarchy.interpretation}
        </div>
      </div>

      {/* Strategic Scenarios */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Target className="w-4 h-4 text-yellow-500" /> Strategic Outcome Scenarios
        </h4>
        <div className="space-y-3">
          {data.scenarios.map((scenario) => (
            <ScenarioCard key={scenario.name} scenario={scenario} isCurrent={scenario.name === data.current_scenario} />
          ))}
        </div>
      </div>

      {/* Equity Stakes */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Globe className="w-4 h-4 text-blue-400" /> Government Equity Stakes
        </h4>
        <div className="space-y-2">
          {data.equity_stakes.map((stake, i) => (
            <EquityStakeRow key={i} stake={stake} />
          ))}
        </div>
      </div>

      {/* Chokepoints */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Factory className="w-4 h-4 text-orange-400" /> Processing & Logistics Chokepoints
        </h4>
        <div className="space-y-2">
          {data.chokepoints.map((cp, i) => (
            <ChokepointRow key={i} chokepoint={cp} />
          ))}
        </div>
      </div>

      {/* Regulatory Actions */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-yellow-400" /> Regulatory Forbearance
        </h4>
        <div className="space-y-2">
          {data.regulatory_actions.map((action, i) => (
            <RegulatoryRow key={i} action={action} />
          ))}
        </div>
      </div>

      {/* DPA Actions */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-red-400" /> Defense Production Act & Priority Allocation
        </h4>
        <div className="space-y-2">
          {data.dpa_actions.map((action, i) => (
            <DPARow key={i} action={action} />
          ))}
        </div>
      </div>

      {/* Bottom Line */}
      <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
        <h4 className="font-bold mb-2 text-white">Bottom Line</h4>
        <p className="text-gray-300 text-sm">
          Markets are no longer the decision-makers — administrators are. Fault.watch now shows who, how, and why — not just what moved.
        </p>
      </div>
    </div>
  )
}

// Scenario Card Component
function ScenarioCard({ scenario, isCurrent }: { scenario: StrategicScenario; isCurrent: boolean }) {
  const riskColors: Record<string, string> = {
    green: 'border-green-500/50 bg-green-900/20',
    yellow: 'border-yellow-500/50 bg-yellow-900/20',
    orange: 'border-orange-500/50 bg-orange-900/20',
    red: 'border-red-500/50 bg-red-900/20',
  }

  return (
    <div className={`p-4 rounded-lg border ${riskColors[scenario.risk_color]} ${isCurrent ? 'ring-2 ring-purple-500' : ''}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white">{scenario.name}</span>
          {isCurrent && <span className="px-2 py-0.5 bg-purple-600 text-white text-xs rounded-full">CURRENT</span>}
        </div>
        <span className="text-xs text-gray-400 uppercase">{scenario.probability}</span>
      </div>
      <p className="text-sm text-gray-300 mb-2">{scenario.description}</p>
      <div className="space-y-1">
        <div className="text-xs text-gray-400">Indicators:</div>
        <div className="flex flex-wrap gap-1">
          {scenario.indicators.map((ind, i) => (
            <span key={i} className="px-2 py-0.5 bg-gray-800 text-xs text-gray-300 rounded">{ind}</span>
          ))}
        </div>
      </div>
      <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-gray-400">
        <strong>Outcome:</strong> {scenario.outcome}
      </div>
    </div>
  )
}

// Equity Stake Row
function EquityStakeRow({ stake }: { stake: EquityStake }) {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium text-white">{stake.entity}</span>
        <ControlBadge level={stake.control_level} />
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-400">
        <span>{stake.government}</span>
        <span>{stake.stake_pct}% stake</span>
        <span className="text-blue-400">{stake.strategic_metal}</span>
      </div>
      <p className="text-xs text-gray-500 mt-1">{stake.notes}</p>
    </div>
  )
}

// Chokepoint Row
function ChokepointRow({ chokepoint }: { chokepoint: ChokepointAsset }) {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium text-white">{chokepoint.name}</span>
        <ControlBadge level={chokepoint.control_level} />
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-400">
        <span>{chokepoint.type}</span>
        <span>{chokepoint.location}</span>
        <span className="text-orange-400">{chokepoint.capacity_pct_global}% global</span>
      </div>
      <p className="text-xs text-gray-500 mt-1">{chokepoint.strategic_significance}</p>
    </div>
  )
}

// Regulatory Action Row
function RegulatoryRow({ action }: { action: RegulatoryAction }) {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white">{action.agency}</span>
          <span className="text-xs text-gray-500">{action.date}</span>
        </div>
        <ControlBadge level={action.control_level} />
      </div>
      <div className="text-sm text-gray-300 mb-1">{action.action_type}: {action.target}</div>
      <div className="text-xs text-gray-400 mb-1">{action.impact}</div>
      <div className="text-xs text-yellow-400/80 bg-yellow-900/20 px-2 py-1 rounded">
        Hidden Signal: {action.hidden_signal}
      </div>
    </div>
  )
}

// DPA Action Row
function DPARow({ action }: { action: DPAAction }) {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white">{action.title}</span>
          {action.explicit && <span className="px-1.5 py-0.5 bg-red-600 text-white text-xs rounded">EXPLICIT</span>}
        </div>
        <ControlBadge level={action.control_level} />
      </div>
      <div className="flex items-center gap-2 text-sm mb-1">
        <span className="text-gray-400">{action.sector}</span>
        <span className="text-gray-500">|</span>
        <span className="text-red-400">{action.metals_affected.join(', ')}</span>
      </div>
      <div className="text-xs text-gray-400 mb-1">
        <strong>Demand:</strong> {action.demand_impact}
      </div>
      <div className="text-xs text-orange-400/80 bg-orange-900/20 px-2 py-1 rounded">
        Civilian Impact: {action.civilian_impact}
      </div>
    </div>
  )
}
