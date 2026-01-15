'use client'

import { useState } from 'react'
import { Radio, RefreshCw, Download, History, ChevronDown, ChevronUp } from 'lucide-react'
import { CrisisScanData, getAlertColor } from '@/lib/crisis-scanner-types'
import { AlertPanel } from './AlertPanel'
import { SilverIndicators } from './SilverIndicators'
import { FedFacilities } from './FedFacilities'
import { BankRiskMatrix } from './BankRiskMatrix'
import { UnverifiedTracker } from './UnverifiedTracker'

interface CrisisScannerProps {
  data: CrisisScanData
}

export function CrisisScanner({ data }: CrisisScannerProps) {
  const [expandedSections, setExpandedSections] = useState({
    silver: true,
    fed: true,
    banks: true,
    unverified: true,
    priorities: false,
    history: false
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  const alertColor = getAlertColor(data.system_status.alert_level)

  return (
    <div className="crisis-scanner">
      {/* Scanner Header */}
      <div className="scanner-header">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full animate-pulse"
              style={{ backgroundColor: alertColor }}
            />
            <h1 className="text-lg font-black tracking-wider text-white">
              FAULT WATCH
            </h1>
            <span className="text-lg font-light text-gray-500">|</span>
            <span className="text-sm font-bold text-amber-400 tracking-widest">
              CRISIS SCANNER
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-[10px] text-gray-500">
            Scan ID: <span className="font-mono text-gray-400">{data.scan_metadata.scan_id}</span>
          </div>
          <div className="text-[10px] text-gray-500">
            v{data.scan_metadata.version}
          </div>
          <button className="scanner-btn">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <button className="scanner-btn">
            <Download className="w-3.5 h-3.5" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Main Alert Panel */}
      <AlertPanel
        systemStatus={data.system_status}
        lastScan={data.scan_metadata.scan_timestamp}
      />

      {/* Silver & Fed Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <CollapsibleSection
          title="SILVER MARKET"
          expanded={expandedSections.silver}
          onToggle={() => toggleSection('silver')}
          accentColor="#F59E0B"
        >
          <SilverIndicators silver={data.silver_market} />
        </CollapsibleSection>

        <CollapsibleSection
          title="FED FACILITIES"
          expanded={expandedSections.fed}
          onToggle={() => toggleSection('fed')}
          accentColor="#3B82F6"
        >
          <FedFacilities fed={data.federal_reserve} />
        </CollapsibleSection>
      </div>

      {/* Bank Risk Matrix - Full Width */}
      <div className="mt-4">
        <CollapsibleSection
          title="BANK SURVEILLANCE"
          expanded={expandedSections.banks}
          onToggle={() => toggleSection('banks')}
          accentColor="#EF4444"
        >
          <BankRiskMatrix banks={data.banks} />
        </CollapsibleSection>
      </div>

      {/* Unverified Claims Tracker */}
      <div className="mt-4">
        <CollapsibleSection
          title="UNVERIFIED CLAIMS"
          expanded={expandedSections.unverified}
          onToggle={() => toggleSection('unverified')}
          accentColor="#EA580C"
          badge={`${data.unverified_claims_watchlist.filter(c => c.status !== 'EFFECTIVELY_DEBUNKED').length} Active`}
        >
          <UnverifiedTracker claims={data.unverified_claims_watchlist} />
        </CollapsibleSection>
      </div>

      {/* Next Scan Priorities */}
      <div className="mt-4">
        <CollapsibleSection
          title="NEXT SCAN PRIORITIES"
          expanded={expandedSections.priorities}
          onToggle={() => toggleSection('priorities')}
          accentColor="#6B7280"
        >
          <div className="scanner-card">
            <div className="space-y-2">
              {data.next_scan_priorities.map((priority, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-2 bg-black/30 rounded border border-gray-800"
                >
                  <span className="w-6 h-6 rounded bg-gray-700 text-gray-400 text-[10px] font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                  <span className="text-sm text-gray-300">{priority}</span>
                </div>
              ))}
            </div>
          </div>
        </CollapsibleSection>
      </div>

      {/* Historical Context */}
      <div className="mt-4">
        <CollapsibleSection
          title="HISTORICAL CONTEXT"
          expanded={expandedSections.history}
          onToggle={() => toggleSection('history')}
          accentColor="#9CA3AF"
        >
          <div className="scanner-card">
            <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-3">
              Bank Manipulation Settlements ({data.historical_context.bank_manipulation_settlements.period_of_manipulation})
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="p-3 bg-black/40 rounded border border-gray-800">
                <div className="text-[9px] text-gray-600 mb-1">Total Fines</div>
                <div className="text-xl font-bold text-amber-400">
                  ${(data.historical_context.bank_manipulation_settlements.total_fines / 1e9).toFixed(2)}B
                </div>
              </div>
              <div className="p-3 bg-black/40 rounded border border-gray-800">
                <div className="text-[9px] text-gray-600 mb-1">Manipulation Period</div>
                <div className="text-lg font-bold text-white">
                  {data.historical_context.bank_manipulation_settlements.period_of_manipulation}
                </div>
              </div>
              <div className="p-3 bg-black/40 rounded border border-gray-800">
                <div className="text-[9px] text-gray-600 mb-1">Prosecution Period</div>
                <div className="text-lg font-bold text-white">
                  {data.historical_context.bank_manipulation_settlements.prosecution_period}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Major Settlements</div>
                <div className="space-y-1">
                  {data.historical_context.bank_manipulation_settlements.major_settlements.map((s, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-black/30 rounded text-sm">
                      <span className="text-gray-300">{s.bank}</span>
                      <span className="text-amber-400 font-mono">${(s.amount / 1e6).toFixed(0)}M</span>
                      <span className="text-gray-600 text-[10px]">{s.year}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Criminal Convictions</div>
                <div className="space-y-1">
                  {data.historical_context.bank_manipulation_settlements.criminal_convictions.map((c, i) => (
                    <div key={i} className="p-2 bg-black/30 rounded text-sm">
                      <div className="text-gray-300">{c.name}</div>
                      <div className="text-[10px] text-gray-500">{c.role}</div>
                      <div className="text-[10px] text-red-400">{c.sentence} ({c.year})</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-4 p-2 bg-gray-500/10 rounded text-[10px] text-gray-500 italic">
              {data.historical_context.bank_manipulation_settlements.note}
            </div>
          </div>
        </CollapsibleSection>
      </div>

      {/* Scanner Footer */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-[10px] text-gray-600">
          <div>
            Analyst: {data.scan_metadata.analyst} | Scan Date: {data.scan_metadata.scan_date}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-500">Module: Crisis Scanner</span>
            <span className="text-gray-700">|</span>
            <span className="text-amber-500/50">fault.watch</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Collapsible Section Component
function CollapsibleSection({
  title,
  expanded,
  onToggle,
  accentColor,
  badge,
  children
}: {
  title: string
  expanded: boolean
  onToggle: () => void
  accentColor: string
  badge?: string
  children: React.ReactNode
}) {
  return (
    <div className="collapsible-section">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 bg-black/40 rounded-t border border-gray-800 hover:bg-black/60 transition-colors"
        style={{ borderLeftColor: accentColor, borderLeftWidth: '3px' }}
      >
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold tracking-wider text-gray-400">{title}</span>
          {badge && (
            <span
              className="text-[9px] px-2 py-0.5 rounded font-bold"
              style={{ backgroundColor: `${accentColor}20`, color: accentColor }}
            >
              {badge}
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
      {expanded && (
        <div className="border-x border-b border-gray-800 rounded-b overflow-hidden">
          {children}
        </div>
      )}
    </div>
  )
}

// Export all components
export { AlertPanel } from './AlertPanel'
export { SilverIndicators } from './SilverIndicators'
export { FedFacilities } from './FedFacilities'
export { BankRiskMatrix } from './BankRiskMatrix'
export { UnverifiedTracker } from './UnverifiedTracker'
