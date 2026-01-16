'use client'

import { useQuery } from '@tanstack/react-query'
import { api, FaultWatchAlertsData, StrategicAlert, AlertCondition, InflectionPoint, AlertSeverity, AlertStatus } from '@/lib/api'
import { AlertTriangle, Shield, Activity, TrendingDown, Clock, CheckCircle, XCircle, Eye, ChevronRight, Target, Zap, Building2, DollarSign } from 'lucide-react'

// Severity colors
const severityColors: Record<AlertSeverity, { bg: string; text: string; border: string; pulse?: boolean }> = {
  low: { bg: 'bg-green-900/20', text: 'text-green-400', border: 'border-green-500/30' },
  medium: { bg: 'bg-yellow-900/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  high: { bg: 'bg-orange-900/20', text: 'text-orange-400', border: 'border-orange-500/30' },
  critical: { bg: 'bg-red-900/20', text: 'text-red-400', border: 'border-red-500/30', pulse: true },
}

// Status colors
const statusColors: Record<AlertStatus, { bg: string; text: string }> = {
  inactive: { bg: 'bg-gray-700', text: 'text-gray-400' },
  watching: { bg: 'bg-blue-600', text: 'text-blue-100' },
  triggered: { bg: 'bg-orange-600', text: 'text-orange-100' },
  confirmed: { bg: 'bg-red-600', text: 'text-red-100' },
}

// Alert icons
const alertIcons: Record<string, any> = {
  alert_a: Zap,          // Dealer Control Breaking
  alert_b: Activity,      // Clearing Stress
  alert_c: Building2,     // Funding Contagion
}

// Severity Badge
function SeverityBadge({ severity }: { severity: AlertSeverity }) {
  const colors = severityColors[severity]
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase ${colors.bg} ${colors.text} ${colors.pulse ? 'animate-pulse' : ''}`}>
      {severity}
    </span>
  )
}

// Status Badge
function StatusBadge({ status }: { status: AlertStatus }) {
  const colors = statusColors[status]
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
      {status.toUpperCase()}
    </span>
  )
}

// Progress bar for conditions
function ConditionProgress({ met, required }: { met: number; required: number }) {
  const pct = Math.min((met / required) * 100, 100)
  const isTriggered = met >= required

  return (
    <div className="w-full">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">Conditions</span>
        <span className={isTriggered ? 'text-orange-400 font-bold' : 'text-gray-400'}>
          {met}/{required} {isTriggered && '(TRIGGERED)'}
        </span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${isTriggered ? 'bg-orange-500' : 'bg-blue-500'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// Main card for dashboard
export function FaultWatchAlertsCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['fault-watch-alerts'],
    queryFn: api.getFaultWatchAlerts,
    refetchInterval: 60000, // 1 minute
  })

  if (isLoading || !data) {
    return (
      <div className="card cursor-pointer hover:border-orange-500/50 transition-colors">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  const colors = severityColors[data.overall_alert_level]
  const triggeredAlerts = data.alerts.filter(a => a.status === 'triggered' || a.status === 'confirmed')

  return (
    <div className={`card cursor-pointer hover:border-orange-500/50 transition-colors ${colors.border} border`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-5 h-5 ${colors.text}`} />
          <h3 className="font-bold text-white">Fault-Watch Alerts</h3>
        </div>
        <SeverityBadge severity={data.overall_alert_level} />
      </div>

      {/* System Status Banner */}
      <div className={`${colors.bg} ${colors.text} px-3 py-2 rounded-lg mb-3 text-sm`}>
        <div className="flex items-center justify-between">
          <span className="font-bold">{data.system_status}</span>
          <span className="text-xs opacity-80">{data.market_regime}</span>
        </div>
      </div>

      {/* Alert Summary Grid */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {data.alerts.map((alert) => {
          const Icon = alertIcons[alert.id] || AlertTriangle
          const isTriggered = alert.status === 'triggered' || alert.status === 'confirmed'
          return (
            <div
              key={alert.id}
              className={`text-center p-2 rounded ${isTriggered ? 'bg-orange-900/30 border border-orange-500/30' : 'bg-gray-800/50'}`}
            >
              <Icon className={`w-4 h-4 mx-auto mb-1 ${isTriggered ? 'text-orange-400' : 'text-gray-500'}`} />
              <div className={`text-xs ${isTriggered ? 'text-orange-400 font-bold' : 'text-gray-400'}`}>
                {alert.conditions_met}/{alert.conditions_required}
              </div>
              <div className="text-[10px] text-gray-500 truncate">{alert.subtitle}</div>
            </div>
          )
        })}
      </div>

      {/* Triggered Alerts List */}
      {triggeredAlerts.length > 0 && (
        <div className="space-y-1 mb-3">
          {triggeredAlerts.map((alert) => (
            <div key={alert.id} className="flex items-center gap-2 text-sm">
              <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></span>
              <span className="text-orange-400 font-medium">{alert.name}</span>
            </div>
          ))}
        </div>
      )}

      <div className="text-xs text-gray-500">
        {data.conditions_triggered} conditions detected across {data.alerts_active} active alerts
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 flex items-center gap-1">
        <ChevronRight className="w-3 h-3" />
        Click for detailed alert analysis & inflection points
      </div>
    </div>
  )
}

// Condition Row Component
function ConditionRow({ condition }: { condition: AlertCondition }) {
  return (
    <div className={`p-3 rounded-lg ${condition.detected ? 'bg-orange-900/20 border border-orange-500/30' : 'bg-gray-800/50'}`}>
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-2">
          {condition.detected ? (
            <CheckCircle className="w-4 h-4 text-orange-400" />
          ) : (
            <XCircle className="w-4 h-4 text-gray-500" />
          )}
          <span className={`font-medium ${condition.detected ? 'text-orange-400' : 'text-gray-400'}`}>
            {condition.name}
          </span>
        </div>
        {condition.detected && condition.detection_date && (
          <span className="text-xs text-gray-500">{condition.detection_date}</span>
        )}
      </div>
      <p className="text-sm text-gray-400 ml-6 mb-2">{condition.description}</p>
      {condition.evidence && (
        <div className={`ml-6 p-2 rounded text-xs ${condition.detected ? 'bg-orange-900/30 text-orange-300' : 'bg-gray-700 text-gray-400'}`}>
          <strong>Evidence:</strong> {condition.evidence}
        </div>
      )}
      <div className="ml-6 mt-1 text-[10px] text-gray-500">
        Source: {condition.data_source}
      </div>
    </div>
  )
}

// Alert Card Component
function AlertCard({ alert }: { alert: StrategicAlert }) {
  const Icon = alertIcons[alert.id] || AlertTriangle
  const isTriggered = alert.status === 'triggered' || alert.status === 'confirmed'
  const colors = severityColors[alert.severity]

  return (
    <div className={`p-4 rounded-lg border ${colors.border} ${colors.bg}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <Icon className={`w-6 h-6 ${colors.text}`} />
          <div>
            <h4 className="font-bold text-white">{alert.name}</h4>
            <span className="text-xs text-gray-400">{alert.subtitle}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <SeverityBadge severity={alert.severity} />
          <StatusBadge status={alert.status} />
        </div>
      </div>

      <p className="text-sm text-gray-300 mb-4">{alert.description}</p>

      <ConditionProgress met={alert.conditions_met} required={alert.conditions_required} />

      <div className="mt-4 space-y-2">
        {alert.conditions.map((condition) => (
          <ConditionRow key={condition.id} condition={condition} />
        ))}
      </div>

      <div className={`mt-4 p-3 rounded-lg ${colors.bg}`}>
        <h5 className={`font-semibold mb-2 ${colors.text}`}>Interpretation</h5>
        <p className="text-sm text-gray-300">{alert.interpretation}</p>
      </div>

      <div className="mt-4">
        <h5 className="font-semibold mb-2 text-gray-400 text-sm">Action Items</h5>
        <ul className="space-y-1">
          {alert.action_items.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
              <ChevronRight className="w-3 h-3 text-blue-400 mt-0.5" />
              {item}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-[10px] text-gray-500">
        Trigger window: {alert.trigger_window_days} days | Updated: {new Date(alert.last_updated).toLocaleString()}
      </div>
    </div>
  )
}

// Inflection Point Card
function InflectionPointCard({ point }: { point: InflectionPoint }) {
  const statusColors: Record<string, string> = {
    'APPROACHING': 'bg-orange-600 text-orange-100',
    'EARLY SIGNALS': 'bg-yellow-600 text-yellow-100',
    'NOT YET': 'bg-gray-600 text-gray-200',
  }

  return (
    <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h5 className="font-bold text-white">{point.name}</h5>
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[point.current_status] || 'bg-gray-600'}`}>
          {point.current_status}
        </span>
      </div>
      <p className="text-sm text-gray-400 mb-3">{point.description}</p>

      <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
        <div className="p-2 bg-gray-700/50 rounded">
          <span className="text-gray-500">Probability</span>
          <div className="font-bold text-orange-400">{point.probability}</div>
        </div>
        <div className="p-2 bg-gray-700/50 rounded">
          <span className="text-gray-500">Timeline</span>
          <div className="font-bold text-blue-400">{point.timeline}</div>
        </div>
      </div>

      <div className="mb-3">
        <span className="text-xs text-gray-500">Indicators:</span>
        <div className="flex flex-wrap gap-1 mt-1">
          {point.indicators.map((ind, i) => (
            <span key={i} className="px-2 py-0.5 bg-gray-700 text-xs text-gray-300 rounded">{ind}</span>
          ))}
        </div>
      </div>

      <div className="p-2 bg-blue-900/20 rounded text-xs text-blue-300 border border-blue-500/30">
        <Eye className="w-3 h-3 inline mr-1" />
        <strong>What to Watch:</strong> {point.what_to_watch}
      </div>
    </div>
  )
}

// Detail view for modal
export function FaultWatchAlertsDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['fault-watch-alerts'],
    queryFn: api.getFaultWatchAlerts,
  })

  if (isLoading || !data) {
    return <div className="text-gray-400">Loading alert data...</div>
  }

  const colors = severityColors[data.overall_alert_level]

  return (
    <div className="space-y-6">
      {/* System Status Banner */}
      <div className={`p-4 rounded-lg border ${colors.border} ${colors.bg}`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className={`w-6 h-6 ${colors.text}`} />
            <span className={`text-xl font-bold ${colors.text}`}>{data.system_status}</span>
          </div>
          <SeverityBadge severity={data.overall_alert_level} />
        </div>
        <div className="text-lg font-medium text-white mb-1">{data.market_regime}</div>
        <p className="text-sm text-gray-300">{data.regime_description}</p>
        <div className="mt-3 pt-3 border-t border-gray-600 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Active Alerts:</span>
            <span className={`ml-2 font-bold ${colors.text}`}>{data.alerts_active}</span>
          </div>
          <div>
            <span className="text-gray-400">Conditions Triggered:</span>
            <span className={`ml-2 font-bold ${colors.text}`}>{data.conditions_triggered}</span>
          </div>
        </div>
      </div>

      {/* Strategic Alerts */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Zap className="w-5 h-5 text-orange-400" /> Strategic Alerts
        </h4>
        <div className="space-y-4">
          {data.alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      </div>

      {/* Inflection Points */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Target className="w-5 h-5 text-purple-400" /> Inflection Points
        </h4>
        <p className="text-sm text-gray-400 mb-4">
          The repricing event won't be "silver hits $___." It will be one of these structural breaks:
        </p>
        <div className="space-y-4">
          {data.inflection_points.map((point) => (
            <InflectionPointCard key={point.id} point={point} />
          ))}
        </div>
      </div>

      {/* Bottom Line */}
      <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
        <h4 className="font-bold mb-2 text-white">Regime Transition Signal</h4>
        <p className="text-gray-300 text-sm">
          When the "managed stability" regime flips into forced repricing, the transition point will be unmistakable:
          paper-to-physical linkage breaks, clearinghouse containment becomes visible, or bank funding stress becomes market-obvious.
          The alerts above track each pathway to that inflection.
        </p>
      </div>
    </div>
  )
}
