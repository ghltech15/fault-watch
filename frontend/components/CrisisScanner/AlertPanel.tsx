'use client'

import { AlertTriangle, Shield, Eye, Radio, Clock } from 'lucide-react'
import { SystemStatus, AlertLevel, getAlertColor, ALERT_LEVELS } from '@/lib/crisis-scanner-types'

interface AlertPanelProps {
  systemStatus: SystemStatus
  lastScan: string
}

function AlertLevelDisplay({ level }: { level: AlertLevel }) {
  const color = getAlertColor(level)
  const config = Object.values(ALERT_LEVELS).find(c => c.name === level)

  const levelConfigs: Record<AlertLevel, { pulse: boolean; glow: boolean }> = {
    CRITICAL: { pulse: true, glow: true },
    HIGH: { pulse: true, glow: false },
    ELEVATED: { pulse: false, glow: false },
    MODERATE: { pulse: false, glow: false },
    LOW: { pulse: false, glow: false }
  }

  const { pulse, glow } = levelConfigs[level]

  return (
    <div
      className={`relative p-4 rounded-lg border-2 ${pulse ? 'animate-pulse' : ''}`}
      style={{
        borderColor: color,
        backgroundColor: `${color}10`,
        boxShadow: glow ? `0 0 30px ${color}40` : 'none'
      }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-black"
            style={{ backgroundColor: `${color}30`, color }}
          >
            {config?.icon || level[0]}
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider text-gray-500">System Alert Level</div>
            <div className="text-2xl font-black" style={{ color }}>
              {level}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Action Required</div>
          <div className="text-sm font-bold" style={{ color }}>
            {config?.action || 'MONITOR'}
          </div>
        </div>
      </div>

      {config && (
        <div className="mt-3 text-[11px] text-gray-400">
          {config.description}
        </div>
      )}
    </div>
  )
}

export function AlertPanel({ systemStatus, lastScan }: AlertPanelProps) {
  const { alert_level, primary_drivers, recommended_action } = systemStatus

  return (
    <div className="scanner-card border-2" style={{ borderColor: `${getAlertColor(alert_level)}40` }}>
      <div className="scanner-card-header">
        <div className="flex items-center gap-2">
          <div className="scanner-icon-box" style={{ backgroundColor: `${getAlertColor(alert_level)}20` }}>
            <Radio className="w-4 h-4" style={{ color: getAlertColor(alert_level) }} />
          </div>
          <h3 className="scanner-card-title">CRISIS SCANNER STATUS</h3>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-gray-500">
          <Clock className="w-3 h-3" />
          <span>Last scan: {new Date(lastScan).toLocaleString()}</span>
        </div>
      </div>

      <AlertLevelDisplay level={alert_level} />

      {/* Primary Drivers */}
      <div className="mt-4">
        <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-2">
          <AlertTriangle className="w-3 h-3" />
          Primary Drivers
        </div>
        <div className="space-y-1">
          {primary_drivers.map((driver, i) => (
            <div
              key={i}
              className="flex items-center gap-2 text-sm text-gray-300 p-2 bg-black/30 rounded"
            >
              <span className="w-5 h-5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-bold flex items-center justify-center">
                {i + 1}
              </span>
              {driver}
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Action */}
      <div className="mt-4 p-3 rounded-lg border" style={{
        borderColor: `${getAlertColor(alert_level)}40`,
        backgroundColor: `${getAlertColor(alert_level)}05`
      }}>
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4" style={{ color: getAlertColor(alert_level) }} />
          <span className="text-[10px] uppercase tracking-wider text-gray-500">Recommended Action</span>
        </div>
        <div className="text-lg font-bold mt-1" style={{ color: getAlertColor(alert_level) }}>
          {recommended_action}
        </div>
      </div>

      {/* Alert Level Legend */}
      <div className="mt-4 pt-3 border-t border-gray-800">
        <div className="text-[9px] uppercase tracking-wider text-gray-600 mb-2">Alert Level Scale</div>
        <div className="flex items-center gap-1 text-[9px]">
          {(['LOW', 'MODERATE', 'ELEVATED', 'HIGH', 'CRITICAL'] as AlertLevel[]).map(level => (
            <span
              key={level}
              className={`px-2 py-1 rounded ${level === alert_level ? 'ring-1 ring-white/30' : ''}`}
              style={{
                backgroundColor: `${getAlertColor(level)}20`,
                color: getAlertColor(level)
              }}
            >
              {level}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
