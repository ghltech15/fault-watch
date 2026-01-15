'use client'

import { Building, AlertTriangle, Shield, HelpCircle } from 'lucide-react'
import { Banks, BankProfile, RiskLevel, getRiskColor, formatLargeNumber } from '@/lib/crisis-scanner-types'
import { VerificationBadge } from '@/components/VerificationBadge'

interface BankRiskMatrixProps {
  banks: Banks
}

function RiskIndicator({ level, verified = true }: { level: RiskLevel; verified?: boolean }) {
  const color = getRiskColor(level)
  const bgColors: Record<RiskLevel, string> = {
    CRITICAL: 'bg-red-500/20',
    HIGH: 'bg-orange-500/20',
    ELEVATED: 'bg-amber-500/20',
    MODERATE: 'bg-emerald-500/20',
    LOW: 'bg-gray-500/20',
    UNKNOWN: 'bg-gray-500/10'
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold ${bgColors[level]}`}
      style={{ color }}
    >
      {level}
      {!verified && <span className="text-[8px] opacity-60">*</span>}
    </span>
  )
}

function BankRow({ name, bank }: { name: string; bank: BankProfile }) {
  const silverVerified = bank.silver_exposure.verification_status === 'VERIFIED'
  const liquidityVerified = bank.liquidity_risk?.verification_status === 'VERIFIED'

  return (
    <tr className="border-b border-gray-800/50 hover:bg-white/[0.02] transition-colors">
      <td className="py-2 px-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-gray-400">{bank.ticker}</span>
          <span className="text-sm text-white">{name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
        </div>
      </td>
      <td className="py-2 px-3">
        <RiskIndicator level={bank.silver_exposure.risk_level} verified={silverVerified} />
      </td>
      <td className="py-2 px-3">
        <RiskIndicator level={bank.liquidity_risk?.risk_level || 'UNKNOWN'} verified={liquidityVerified} />
      </td>
      <td className="py-2 px-3">
        <RiskIndicator level={bank.overall_crisis_risk} />
      </td>
      <td className="py-2 px-3 text-right">
        <StatusBadge risk={bank.overall_crisis_risk} />
      </td>
    </tr>
  )
}

function StatusBadge({ risk }: { risk: RiskLevel }) {
  const configs: Record<RiskLevel, { label: string; color: string; bg: string }> = {
    CRITICAL: { label: 'ALERT', color: 'text-red-400', bg: 'bg-red-500/20 border-red-500/40' },
    HIGH: { label: 'MONITOR', color: 'text-orange-400', bg: 'bg-orange-500/20 border-orange-500/40' },
    ELEVATED: { label: 'WATCH', color: 'text-amber-400', bg: 'bg-amber-500/20 border-amber-500/40' },
    MODERATE: { label: 'STABLE', color: 'text-emerald-400', bg: 'bg-emerald-500/20 border-emerald-500/40' },
    LOW: { label: 'STABLE', color: 'text-gray-400', bg: 'bg-gray-500/20 border-gray-500/40' },
    UNKNOWN: { label: 'N/A', color: 'text-gray-500', bg: 'bg-gray-500/10 border-gray-500/20' }
  }

  const config = configs[risk]
  return (
    <span className={`text-[9px] font-bold px-2 py-1 rounded border ${config.bg} ${config.color}`}>
      {config.label}
    </span>
  )
}

export function BankRiskMatrix({ banks }: BankRiskMatrixProps) {
  const bankEntries = Object.entries(banks) as [string, BankProfile][]

  // Sort by overall risk (CRITICAL first)
  const riskOrder: RiskLevel[] = ['CRITICAL', 'HIGH', 'ELEVATED', 'MODERATE', 'LOW', 'UNKNOWN']
  const sortedBanks = bankEntries.sort((a, b) => {
    return riskOrder.indexOf(a[1].overall_crisis_risk) - riskOrder.indexOf(b[1].overall_crisis_risk)
  })

  // Count unverified silver claims
  const unverifiedCount = bankEntries.filter(
    ([_, bank]) => bank.silver_exposure.verification_status !== 'VERIFIED'
  ).length

  return (
    <div className="scanner-card">
      <div className="scanner-card-header">
        <div className="flex items-center gap-2">
          <div className="scanner-icon-box">
            <Building className="w-4 h-4" />
          </div>
          <h3 className="scanner-card-title">BANK RISK MATRIX</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[9px] text-gray-500">{bankEntries.length} banks monitored</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-2 px-3 text-[10px] uppercase tracking-wider text-gray-500 font-medium">Bank</th>
              <th className="text-left py-2 px-3 text-[10px] uppercase tracking-wider text-gray-500 font-medium">Silver</th>
              <th className="text-left py-2 px-3 text-[10px] uppercase tracking-wider text-gray-500 font-medium">Liquidity</th>
              <th className="text-left py-2 px-3 text-[10px] uppercase tracking-wider text-gray-500 font-medium">Overall</th>
              <th className="text-right py-2 px-3 text-[10px] uppercase tracking-wider text-gray-500 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedBanks.map(([name, bank]) => (
              <BankRow key={name} name={name} bank={bank} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend & Disclaimer */}
      <div className="mt-4 pt-3 border-t border-gray-800">
        <div className="flex items-start gap-2 text-[9px] text-gray-500">
          <AlertTriangle className="w-3 h-3 text-orange-400 flex-shrink-0 mt-0.5" />
          <span>
            <span className="text-orange-400">*</span> = UNVERIFIED - based on single-source reporting.
            {unverifiedCount} of {bankEntries.length} silver exposure ratings are unverified.
          </span>
        </div>
      </div>

      {/* Highlighted Banks with Concerns */}
      <div className="mt-4 space-y-2">
        {sortedBanks.slice(0, 3).map(([name, bank]) => {
          if (bank.overall_crisis_risk === 'LOW' || bank.overall_crisis_risk === 'MODERATE') return null

          return (
            <div key={name} className="p-2 bg-black/40 rounded border border-gray-800">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-amber-400">{bank.ticker}</span>
                <RiskIndicator level={bank.overall_crisis_risk} />
              </div>
              {bank.risk_note && (
                <div className="text-[10px] text-gray-400">{bank.risk_note}</div>
              )}
              {bank.whistleblower_allegations && (
                <div className="text-[9px] text-orange-400/80 mt-1">
                  Whistleblower: {bank.whistleblower_allegations.claim.substring(0, 60)}...
                </div>
              )}
              {bank.liquidity_risk?.unrealized_bond_losses && (
                <div className="text-[9px] text-red-400/80 mt-1">
                  Unrealized losses: {formatLargeNumber(bank.liquidity_risk.unrealized_bond_losses)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
