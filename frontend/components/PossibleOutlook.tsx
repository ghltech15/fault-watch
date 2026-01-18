'use client'

import { useQuery } from '@tanstack/react-query'
import { api, PossibleOutlookData, BankDomino, CascadePhase, TierIndicator, TimelineEvent } from '@/lib/api'
import {
  Target, TrendingUp, AlertTriangle, CheckCircle2, Circle, Clock,
  ChevronRight, Calendar, Building2, Zap, Shield, Crown, ToggleLeft, ToggleRight,
  CircleDot, Timer, DollarSign
} from 'lucide-react'
import { useState } from 'react'

// Status colors for dominoes
const getDominoStatusColor = (status: string) => {
  switch (status) {
    case 'insolvent': return { bg: 'bg-red-900/50', text: 'text-red-400', border: 'border-red-500/50' }
    case 'critical': return { bg: 'bg-red-900/30', text: 'text-red-400', border: 'border-red-500/30' }
    case 'warning': return { bg: 'bg-orange-900/30', text: 'text-orange-400', border: 'border-orange-500/30' }
    case 'survivor': return { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-500/30' }
    default: return { bg: 'bg-gray-800/50', text: 'text-gray-400', border: 'border-gray-600/30' }
  }
}

// Phase status colors
const getPhaseStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return { bg: 'bg-red-900/40', text: 'text-red-400', icon: CheckCircle2 }
    case 'active': return { bg: 'bg-orange-900/40', text: 'text-orange-400', icon: CircleDot }
    default: return { bg: 'bg-gray-800/30', text: 'text-gray-500', icon: Circle }
  }
}

// Timeline status colors
const getTimelineColor = (status: string) => {
  switch (status) {
    case 'past': return 'text-gray-500 border-gray-600'
    case 'today': return 'text-orange-400 border-orange-500 bg-orange-900/20'
    case 'upcoming': return 'text-yellow-400 border-yellow-500/50'
    default: return 'text-gray-400 border-gray-600/50'
  }
}

// Thesis stage badge
function ThesisStageBadge({ stage }: { stage: string }) {
  const stageConfig: Record<string, { label: string; color: string }> = {
    'pre-cascade': { label: 'PRE-CASCADE', color: 'bg-blue-900/50 text-blue-400 border-blue-500/30' },
    'early-cascade': { label: 'EARLY CASCADE', color: 'bg-yellow-900/50 text-yellow-400 border-yellow-500/30' },
    'mid-cascade': { label: 'MID-CASCADE', color: 'bg-orange-900/50 text-orange-400 border-orange-500/30' },
    'resolution': { label: 'RESOLUTION', color: 'bg-red-900/50 text-red-400 border-red-500/30' },
  }
  const config = stageConfig[stage] || stageConfig['pre-cascade']

  return (
    <span className={`px-2 py-0.5 text-xs font-bold rounded border ${config.color}`}>
      {config.label}
    </span>
  )
}

// Bank Domino Row (compact for card)
function BankDominoRow({ domino, silverPrice }: { domino: BankDomino; silverPrice: number }) {
  const colors = getDominoStatusColor(domino.status)
  const progressPct = Math.min(100, (silverPrice / domino.insolvency_threshold) * 100)

  return (
    <div className={`flex items-center justify-between py-1.5 px-2 rounded ${colors.bg} border ${colors.border}`}>
      <div className="flex items-center gap-2">
        {domino.status === 'insolvent' ? (
          <CheckCircle2 className="w-4 h-4 text-red-400" />
        ) : domino.status === 'survivor' ? (
          <Crown className="w-4 h-4 text-green-400" />
        ) : (
          <Circle className="w-4 h-4 text-gray-500" />
        )}
        <span className={`text-sm font-medium ${colors.text}`}>{domino.name}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">${domino.insolvency_threshold}</span>
        <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full ${progressPct >= 95 ? 'bg-red-500' : progressPct >= 85 ? 'bg-orange-500' : 'bg-gray-500'}`}
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>
    </div>
  )
}

// Tier Indicator Summary
function TierSummary({ tier, triggered, total, label }: { tier: number; triggered: number; total: number; label: string }) {
  const isActive = triggered > 0
  return (
    <div className={`text-center p-2 rounded ${isActive ? 'bg-red-900/30' : 'bg-gray-800/30'}`}>
      <div className={`text-lg font-bold ${isActive ? 'text-red-400' : 'text-gray-500'}`}>
        {triggered}/{total}
      </div>
      <div className="text-[10px] text-gray-500">{label}</div>
    </div>
  )
}

// Main Dashboard Card
export function PossibleOutlookCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['possible-outlook'],
    queryFn: () => api.getPossibleOutlook('A'),
    refetchInterval: 60000, // 1 minute
  })

  if (isLoading || !data) {
    return (
      <div className="card cursor-pointer hover:border-cyan-500/50 transition-colors">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-32 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="card cursor-pointer hover:border-cyan-500/50 transition-colors border border-cyan-500/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-white">Possible Outlook</h3>
        </div>
        <ThesisStageBadge stage={data.thesis_stage} />
      </div>

      {/* Silver Price Context */}
      <div className="bg-gray-800/50 rounded-lg px-3 py-2 mb-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Silver Price</span>
          <span className="text-lg font-bold text-white">${data.current_silver_price.toFixed(2)}</span>
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-gray-500">Days into Sprint</span>
          <span className="text-sm text-cyan-400">{data.days_into_sprint} / 20</span>
        </div>
      </div>

      {/* Bank Dominoes Checklist */}
      <div className="mb-3">
        <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
          <Building2 className="w-3 h-3" /> BANK DOMINOES ({data.dominoes_fallen}/{data.bank_dominoes.length} fallen)
        </div>
        <div className="space-y-1">
          {data.bank_dominoes.map((domino, i) => (
            <BankDominoRow key={i} domino={domino} silverPrice={data.current_silver_price} />
          ))}
        </div>
      </div>

      {/* Tier Indicators Summary */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <TierSummary tier={1} triggered={data.tier1_triggered} total={data.tier1_indicators.length} label="Tier 1" />
        <TierSummary tier={2} triggered={data.tier2_triggered} total={data.tier2_indicators.length} label="Tier 2" />
        <TierSummary tier={3} triggered={data.tier3_triggered} total={data.tier3_indicators.length} label="Tier 3" />
      </div>

      {/* Next Event */}
      {data.timeline.find(t => t.status === 'today' || t.status === 'upcoming') && (
        <div className="bg-orange-900/20 rounded px-3 py-2 mb-3">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-orange-400" />
            <span className="text-xs text-orange-400 font-semibold">
              {data.timeline.find(t => t.status === 'today')?.event ||
               data.timeline.find(t => t.status === 'upcoming')?.event}
            </span>
          </div>
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 flex items-center gap-1">
        <ChevronRight className="w-3 h-3" />
        Click for full thesis, timeline & JPM analysis
      </div>
    </div>
  )
}

// Full Detail View Component
export function PossibleOutlookDetailView() {
  const [selectedTheory, setSelectedTheory] = useState<'A' | 'B'>('A')

  const { data, isLoading } = useQuery({
    queryKey: ['possible-outlook', selectedTheory],
    queryFn: () => api.getPossibleOutlook(selectedTheory),
  })

  if (isLoading || !data) {
    return <div className="text-gray-400">Loading thesis data...</div>
  }

  const currentTheory = selectedTheory === 'A' ? data.jpmorgan_theory.theory_a : data.jpmorgan_theory.theory_b

  return (
    <div className="space-y-6">
      {/* Header with Stage */}
      <div className="p-4 rounded-lg bg-cyan-900/20 border border-cyan-500/30">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Target className="w-6 h-6 text-cyan-400" />
            <span className="text-xl font-bold text-cyan-400">The Controlled Demolition Thesis</span>
          </div>
          <ThesisStageBadge stage={data.thesis_stage} />
        </div>
        <p className="text-gray-300 text-sm">
          Why bailout is politically impossible, and the cleaner play is to let banks fail and consolidate.
        </p>
        <div className="mt-3 flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-white" />
            <span className="text-white font-bold">${data.current_silver_price.toFixed(2)}</span>
            <span className="text-gray-500">Silver</span>
          </div>
          <div className="flex items-center gap-2">
            <Timer className="w-4 h-4 text-cyan-400" />
            <span className="text-cyan-400">Day {data.days_into_sprint}</span>
            <span className="text-gray-500">of Sprint</span>
          </div>
        </div>
      </div>

      {/* Political Factors - Why Bailout Impossible */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Shield className="w-5 h-5 text-purple-400" /> Why Bailout Is Politically Impossible
          <span className="ml-auto text-sm text-purple-400">{data.bailout_impossible_score}% confirmed</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {data.political_factors.map((factor, i) => (
            <div key={i} className={`p-3 rounded-lg border ${factor.status ? 'bg-purple-900/20 border-purple-500/30' : 'bg-gray-800/30 border-gray-600/30'}`}>
              <div className="flex items-start gap-2">
                {factor.status ? (
                  <CheckCircle2 className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                )}
                <div>
                  <div className={`text-sm ${factor.status ? 'text-purple-300' : 'text-gray-400'}`}>
                    {factor.description}
                  </div>
                  {factor.detail && (
                    <div className="text-xs text-gray-500 mt-1">{factor.detail}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bank Dominoes */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Building2 className="w-5 h-5 text-red-400" /> Bank Dominoes
          <span className="ml-auto text-sm text-red-400">{data.dominoes_fallen}/{data.bank_dominoes.length} fallen</span>
        </h4>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="grid grid-cols-12 gap-2 pb-2 border-b border-gray-600 mb-2 text-xs text-gray-500">
            <div className="col-span-3">BANK</div>
            <div className="col-span-2 text-center">TICKER</div>
            <div className="col-span-2 text-center">THRESHOLD</div>
            <div className="col-span-2 text-center">DISTANCE</div>
            <div className="col-span-3 text-center">STATUS</div>
          </div>
          {data.bank_dominoes.map((domino, i) => {
            const colors = getDominoStatusColor(domino.status)
            return (
              <div key={i} className="grid grid-cols-12 gap-2 py-2 border-b border-gray-700/50 items-center">
                <div className="col-span-3 flex items-center gap-2">
                  {domino.is_survivor_candidate && <Crown className="w-3 h-3 text-yellow-400" />}
                  <span className="text-sm text-gray-300">{domino.name}</span>
                </div>
                <div className="col-span-2 text-center text-sm text-gray-400">{domino.ticker}</div>
                <div className="col-span-2 text-center text-sm text-white font-mono">${domino.insolvency_threshold}</div>
                <div className="col-span-2 text-center text-sm text-gray-400">
                  {domino.distance_to_threshold && domino.distance_to_threshold > 0
                    ? `$${domino.distance_to_threshold.toFixed(2)}`
                    : 'CROSSED'}
                </div>
                <div className={`col-span-3 text-center py-1 rounded text-xs font-bold ${colors.bg} ${colors.text}`}>
                  {domino.status.toUpperCase()}
                </div>
              </div>
            )
          })}
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Survivor Bank: <span className="text-green-400 font-semibold">{data.survivor_bank}</span> — Last to fall at ${data.bank_dominoes.find(b => b.is_survivor_candidate)?.insolvency_threshold}
        </div>
      </div>

      {/* Cascade Phases */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Zap className="w-5 h-5 text-orange-400" /> Cascade Timeline
        </h4>
        <div className="space-y-2">
          {data.cascade_phases.map((phase, i) => {
            const config = getPhaseStatusColor(phase.status)
            const Icon = config.icon
            return (
              <div key={i} className={`p-3 rounded-lg border border-gray-700 ${config.bg}`}>
                <div className="flex items-start gap-3">
                  <Icon className={`w-5 h-5 ${config.text} mt-0.5 flex-shrink-0`} />
                  <div className="flex-1">
                    <div className={`font-semibold ${config.text}`}>{phase.name}</div>
                    <div className="text-sm text-gray-400 mt-1">{phase.description}</div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {phase.indicators.map((ind, j) => (
                        <span key={j} className="text-xs px-2 py-0.5 bg-gray-800 rounded text-gray-400">
                          {ind}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 2-Week Sprint Timeline */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Calendar className="w-5 h-5 text-blue-400" /> 2-Week Sprint: {data.sprint_start_date} → {data.sprint_end_date}
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs border-b border-gray-700">
                <th className="text-left py-2 px-2">DATE</th>
                <th className="text-left py-2 px-2">DAY</th>
                <th className="text-left py-2 px-2">EVENT</th>
                <th className="text-right py-2 px-2">PRICE TARGET</th>
              </tr>
            </thead>
            <tbody>
              {data.timeline.map((event, i) => (
                <tr key={i} className={`border-b border-gray-800 ${getTimelineColor(event.status)}`}>
                  <td className="py-2 px-2 font-mono">{event.date}</td>
                  <td className="py-2 px-2">{event.day}</td>
                  <td className="py-2 px-2">{event.event}</td>
                  <td className="py-2 px-2 text-right font-mono">{event.price_target || '---'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tier Indicators */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <AlertTriangle className="w-5 h-5 text-yellow-400" /> Tier Indicators
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Tier 1 */}
          <div className="p-3 rounded-lg border border-blue-500/30 bg-blue-900/10">
            <div className="text-sm font-semibold text-blue-400 mb-2">
              Tier 1: Sunday-Monday ({data.tier1_triggered}/{data.tier1_indicators.length})
            </div>
            <div className="space-y-1">
              {data.tier1_indicators.map((ind, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  {ind.triggered ? (
                    <CheckCircle2 className="w-3 h-3 text-red-400" />
                  ) : (
                    <Circle className="w-3 h-3 text-gray-500" />
                  )}
                  <span className={ind.triggered ? 'text-red-400' : 'text-gray-400'}>{ind.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tier 2 */}
          <div className="p-3 rounded-lg border border-yellow-500/30 bg-yellow-900/10">
            <div className="text-sm font-semibold text-yellow-400 mb-2">
              Tier 2: Mon-Tue ({data.tier2_triggered}/{data.tier2_indicators.length})
            </div>
            <div className="space-y-1">
              {data.tier2_indicators.map((ind, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  {ind.triggered ? (
                    <CheckCircle2 className="w-3 h-3 text-red-400" />
                  ) : (
                    <Circle className="w-3 h-3 text-gray-500" />
                  )}
                  <span className={ind.triggered ? 'text-red-400' : 'text-gray-400'}>{ind.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tier 3 */}
          <div className="p-3 rounded-lg border border-red-500/30 bg-red-900/10">
            <div className="text-sm font-semibold text-red-400 mb-2">
              Tier 3: Confirmation ({data.tier3_triggered}/{data.tier3_indicators.length})
            </div>
            <div className="space-y-1">
              {data.tier3_indicators.map((ind, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  {ind.triggered ? (
                    <CheckCircle2 className="w-3 h-3 text-red-400" />
                  ) : (
                    <Circle className="w-3 h-3 text-gray-500" />
                  )}
                  <span className={ind.triggered ? 'text-red-400' : 'text-gray-400'}>{ind.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* JPMorgan Theory Toggle */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold flex items-center gap-2 text-white">
            <Crown className="w-5 h-5 text-yellow-400" /> The JPMorgan Question
          </h4>
          <button
            onClick={() => setSelectedTheory(selectedTheory === 'A' ? 'B' : 'A')}
            className="flex items-center gap-2 px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            {selectedTheory === 'A' ? (
              <ToggleLeft className="w-5 h-5 text-green-400" />
            ) : (
              <ToggleRight className="w-5 h-5 text-orange-400" />
            )}
            <span className="text-sm text-gray-300">Theory {selectedTheory}</span>
          </button>
        </div>

        <div className={`p-4 rounded-lg border ${selectedTheory === 'A' ? 'border-green-500/30 bg-green-900/10' : 'border-orange-500/30 bg-orange-900/10'}`}>
          <div className={`text-lg font-bold mb-2 ${selectedTheory === 'A' ? 'text-green-400' : 'text-orange-400'}`}>
            Theory {selectedTheory}: {currentTheory.name}
          </div>
          <p className="text-gray-300 mb-3">{currentTheory.description}</p>
          <div className="space-y-1">
            {currentTheory.evidence.map((ev, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-400">
                <ChevronRight className="w-3 h-3" />
                {ev}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-3 p-3 rounded bg-gray-800/50">
          <div className="text-xs text-gray-500 mb-2">Current Evidence (Either Theory):</div>
          <div className="space-y-1">
            {data.jpmorgan_theory.current_evidence.map((ev, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-yellow-400">
                <Zap className="w-3 h-3" />
                {ev}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Price Targets */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <TrendingUp className="w-5 h-5 text-green-400" /> Price Targets
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {data.price_targets.map((target, i) => {
            const isReached = data.current_silver_price >= target.price_low
            return (
              <div key={i} className={`p-3 rounded-lg border ${isReached ? 'border-green-500/50 bg-green-900/20' : 'border-gray-600/50 bg-gray-800/30'}`}>
                <div className={`text-sm font-semibold ${isReached ? 'text-green-400' : 'text-gray-300'}`}>
                  {target.label}
                </div>
                <div className="text-2xl font-bold text-white mt-1">
                  ${target.price_low}-${target.price_high}
                </div>
                <div className="text-xs text-gray-500 mt-1">{target.significance}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Inauguration Wildcard */}
      <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30">
        <h4 className="font-semibold mb-2 flex items-center gap-2 text-red-400">
          <AlertTriangle className="w-5 h-5" /> Inauguration Wildcard: {data.inauguration_date}
        </h4>
        <p className="text-sm text-gray-300 mb-3">
          If Trump says ANYTHING that weakens dollar confidence, gold/silver spike on safe haven flow.
          The banks' best hope is Trump staying quiet about the dollar.
        </p>
        <div className="flex flex-wrap gap-2">
          {data.inauguration_factors.map((factor, i) => (
            <span key={i} className="text-xs px-2 py-1 bg-red-900/30 rounded text-red-300">
              {factor}
            </span>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-500 text-center">
        Last Updated: {data.last_updated}
      </div>
    </div>
  )
}
