'use client'

import { useQuery } from '@tanstack/react-query'
import { api, CrisisSearchPadData, RumorEntry, SearchPadBankPosition, KeyDate, SearchPadVerificationStatus } from '@/lib/api'
import { Search, Database, AlertTriangle, Building2, TrendingUp, Calendar, ExternalLink, CheckCircle, XCircle, HelpCircle, AlertCircle, ChevronRight, FileText, Globe, DollarSign, Banknote, Shield } from 'lucide-react'

// Verification status colors and icons
const verificationConfig: Record<SearchPadVerificationStatus, { bg: string; text: string; icon: any; label: string }> = {
  verified: { bg: 'bg-green-900/20', text: 'text-green-400', icon: CheckCircle, label: 'VERIFIED' },
  partial: { bg: 'bg-yellow-900/20', text: 'text-yellow-400', icon: HelpCircle, label: 'PARTIAL' },
  unverified: { bg: 'bg-orange-900/20', text: 'text-orange-400', icon: AlertCircle, label: 'UNVERIFIED' },
  fabricated: { bg: 'bg-red-900/20', text: 'text-red-400', icon: XCircle, label: 'FABRICATED' },
}

// Assessment status colors
const assessmentColors: Record<string, { bg: string; text: string }> = {
  SEVERE: { bg: 'bg-red-900/30', text: 'text-red-400' },
  ELEVATED: { bg: 'bg-orange-900/30', text: 'text-orange-400' },
  WATCHLIST: { bg: 'bg-yellow-900/30', text: 'text-yellow-400' },
  VOLATILE: { bg: 'bg-purple-900/30', text: 'text-purple-400' },
  NORMAL: { bg: 'bg-green-900/30', text: 'text-green-400' },
}

// Verification Badge
function VerificationBadge({ status }: { status: SearchPadVerificationStatus }) {
  const config = verificationConfig[status]
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${config.bg} ${config.text}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

// Assessment Status Badge
function AssessmentBadge({ status, detail }: { status: string; detail: string }) {
  const colors = assessmentColors[status] || assessmentColors.NORMAL
  return (
    <div className={`p-2 rounded-lg ${colors.bg}`}>
      <div className={`font-bold text-sm ${colors.text}`}>{status}</div>
      <div className="text-xs text-gray-400 mt-0.5">{detail}</div>
    </div>
  )
}

// Rumor Card
function RumorCard({ rumor }: { rumor: RumorEntry }) {
  const config = verificationConfig[rumor.verification_status]
  return (
    <div className={`p-3 rounded-lg border ${config.bg} border-gray-700`}>
      <div className="flex items-start justify-between mb-2">
        <h5 className="font-semibold text-white text-sm">{rumor.title}</h5>
        <VerificationBadge status={rumor.verification_status} />
      </div>
      <p className="text-sm text-gray-300 mb-2">{rumor.claim}</p>
      <div className="text-xs text-gray-500 mb-1">
        <span className="text-gray-400">Origin:</span> {rumor.origin}
      </div>
      <div className={`text-xs ${config.text}`}>
        <span className="text-gray-400">Status:</span> {rumor.status_note}
      </div>
    </div>
  )
}

// Bank Position Card
function BankPositionCard({ bank }: { bank: SearchPadBankPosition }) {
  return (
    <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h5 className="font-bold text-white">{bank.bank}</h5>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
          bank.status.toLowerCase().includes('distress') ? 'bg-red-900/50 text-red-400' :
          bank.status.toLowerCase().includes('benefiting') ? 'bg-green-900/50 text-green-400' :
          'bg-blue-900/50 text-blue-400'
        }`}>
          {bank.status.split(' ')[0]}
        </span>
      </div>
      {bank.current_position && (
        <div className="text-sm text-gray-300 mb-1">{bank.current_position}</div>
      )}
      {bank.reported_action && (
        <div className="text-xs text-gray-400 mb-1">
          <span className="text-gray-500">Action:</span> {bank.reported_action}
        </div>
      )}
      {bank.forecast && (
        <div className="text-xs text-blue-400 mb-1">
          <span className="text-gray-500">Forecast:</span> {bank.forecast}
        </div>
      )}
      {bank.stock_price && (
        <div className="text-xs text-gray-500">{bank.stock_price}</div>
      )}
      {bank.rumors && (
        <div className="text-xs text-orange-400 mt-1">
          <AlertTriangle className="w-3 h-3 inline mr-1" />
          Rumor: {bank.rumors}
        </div>
      )}
    </div>
  )
}

// Key Date Card
function KeyDateCard({ date }: { date: KeyDate }) {
  const isToday = date.date.includes('Jan 17') // Quick check for today's date
  return (
    <div className={`p-2 rounded-lg ${isToday ? 'bg-orange-900/30 border border-orange-500/30' : 'bg-gray-800/50'}`}>
      <div className="flex items-center gap-2">
        <Calendar className={`w-4 h-4 ${isToday ? 'text-orange-400' : 'text-gray-500'}`} />
        <div>
          <div className={`font-semibold text-sm ${isToday ? 'text-orange-400' : 'text-white'}`}>{date.date}</div>
          <div className="text-xs text-gray-400">{date.event}</div>
          <div className="text-xs text-gray-500">{date.significance}</div>
        </div>
      </div>
    </div>
  )
}

// Main card for dashboard
export function CrisisSearchPadCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['crisis-search-pad'],
    queryFn: api.getCrisisSearchPad,
    refetchInterval: 300000, // 5 minutes
  })

  if (isLoading || !data) {
    return (
      <div className="card cursor-pointer hover:border-cyan-500/50 transition-colors">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  // Count verification statuses
  const verifiedCount = data.rumors.filter(r => r.verification_status === 'verified').length
  const partialCount = data.rumors.filter(r => r.verification_status === 'partial').length
  const unverifiedCount = data.rumors.filter(r => r.verification_status === 'unverified').length
  const fabricatedCount = data.rumors.filter(r => r.verification_status === 'fabricated').length

  // Get worst assessment status
  const statuses = Object.values(data.current_assessment).map(a => a.status)
  const hasSevere = statuses.includes('SEVERE')
  const hasElevated = statuses.includes('ELEVATED')

  return (
    <div className={`card cursor-pointer hover:border-cyan-500/50 transition-colors ${hasSevere ? 'border-red-500/30 border' : hasElevated ? 'border-orange-500/30 border' : ''}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-white">Crisis Search Pad</h3>
        </div>
        <span className="text-xs text-gray-500">{data.last_updated}</span>
      </div>

      {/* Assessment Grid */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        {Object.entries(data.current_assessment).map(([key, value]) => {
          const colors = assessmentColors[value.status] || assessmentColors.NORMAL
          return (
            <div key={key} className={`p-2 rounded ${colors.bg}`}>
              <div className={`text-xs font-bold ${colors.text}`}>{value.status}</div>
              <div className="text-[10px] text-gray-400 capitalize">{key.replace('_', ' ')}</div>
            </div>
          )
        })}
      </div>

      {/* Tier Summary */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center p-2 bg-green-900/20 rounded">
          <Database className="w-4 h-4 mx-auto mb-1 text-green-400" />
          <div className="text-xs text-green-400 font-bold">Tier 1</div>
          <div className="text-[10px] text-gray-400">Confirmed</div>
        </div>
        <div className="text-center p-2 bg-orange-900/20 rounded">
          <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-orange-400" />
          <div className="text-xs text-orange-400 font-bold">Tier 2</div>
          <div className="text-[10px] text-gray-400">{data.rumors.length} Rumors</div>
        </div>
        <div className="text-center p-2 bg-blue-900/20 rounded">
          <Building2 className="w-4 h-4 mx-auto mb-1 text-blue-400" />
          <div className="text-xs text-blue-400 font-bold">Tier 3</div>
          <div className="text-[10px] text-gray-400">{data.bank_positions.length} Banks</div>
        </div>
      </div>

      {/* Rumor Verification Summary */}
      <div className="flex gap-2 mb-3 text-xs">
        {fabricatedCount > 0 && (
          <span className="px-2 py-0.5 bg-red-900/30 text-red-400 rounded">{fabricatedCount} Fabricated</span>
        )}
        {unverifiedCount > 0 && (
          <span className="px-2 py-0.5 bg-orange-900/30 text-orange-400 rounded">{unverifiedCount} Unverified</span>
        )}
        {partialCount > 0 && (
          <span className="px-2 py-0.5 bg-yellow-900/30 text-yellow-400 rounded">{partialCount} Partial</span>
        )}
      </div>

      {/* Key Dates Preview */}
      {data.key_dates.length > 0 && (
        <div className="text-xs text-gray-400 mb-3">
          <Calendar className="w-3 h-3 inline mr-1" />
          Next: {data.key_dates[0].date} - {data.key_dates[0].event}
        </div>
      )}

      <div className="text-xs text-gray-500">
        {data.daily_metrics.length} daily + {data.monthly_metrics.length} monthly metrics tracked
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 flex items-center gap-1">
        <ChevronRight className="w-3 h-3" />
        Click for full research data, sources & monitoring
      </div>
    </div>
  )
}

// Detail view for modal
export function CrisisSearchPadDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['crisis-search-pad'],
    queryFn: api.getCrisisSearchPad,
  })

  if (isLoading || !data) {
    return <div className="text-gray-400">Loading crisis search pad data...</div>
  }

  return (
    <div className="space-y-6">
      {/* Current Assessment Banner */}
      <div className="p-4 rounded-lg bg-gray-800 border border-gray-700">
        <h4 className="font-bold text-white mb-3 flex items-center gap-2">
          <Shield className="w-5 h-5 text-cyan-400" /> Current Assessment
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(data.current_assessment).map(([key, value]) => (
            <AssessmentBadge key={key} status={value.status} detail={value.detail} />
          ))}
        </div>
        <div className="mt-3 text-xs text-gray-500">Last Updated: {data.last_updated}</div>
      </div>

      {/* Key Dates */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
          <Calendar className="w-5 h-5 text-orange-400" /> Key Dates to Watch
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {data.key_dates.map((date, i) => (
            <KeyDateCard key={i} date={date} />
          ))}
        </div>
      </div>

      {/* TIER 1: Confirmed Data */}
      <div className="p-4 bg-green-900/10 rounded-lg border border-green-500/30">
        <h4 className="font-bold text-green-400 mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" /> TIER 1: Confirmed/Verifiable Data
        </h4>

        {/* Fed Repo Activity */}
        <div className="mb-4">
          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
            <Banknote className="w-4 h-4 text-blue-400" /> Fed Repo Activity
          </h5>
          <div className="bg-gray-800/50 rounded p-3 mb-2">
            <div className="text-sm text-blue-400 mb-2">{data.fed_repo_key_change}</div>
            <div className="space-y-2">
              {data.fed_repo_activity.map((entry, i) => (
                <div key={i} className="flex justify-between text-sm">
                  <span className="text-gray-400">{entry.date}</span>
                  <span className="text-white font-mono">{entry.amount}</span>
                  <span className="text-gray-500 text-xs">{entry.notes}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="text-xs text-gray-500">Sources: {data.fed_repo_sources.join(', ')}</div>
        </div>

        {/* COMEX Delivery Stress */}
        <div className="mb-4">
          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4 text-orange-400" /> COMEX Delivery Stress
          </h5>
          <div className="space-y-2">
            {data.comex_delivery_stress.map((entry, i) => (
              <div key={i} className="bg-gray-800/50 rounded p-2">
                <div className="flex justify-between mb-1">
                  <span className="text-white font-medium text-sm">{entry.event}</span>
                  <span className="text-gray-500 text-xs">{entry.date}</span>
                </div>
                <div className="text-xs text-gray-400">{entry.details}</div>
              </div>
            ))}
          </div>
          <div className="text-xs text-gray-500 mt-2">Sources: {data.comex_sources.join(', ')}</div>
        </div>

        {/* LBMA Data */}
        <div className="mb-4">
          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
            <Globe className="w-4 h-4 text-purple-400" /> LBMA Vault Data
          </h5>
          <div className="bg-gray-800/50 rounded p-3 mb-2">
            <div className="text-sm text-purple-400 mb-2">{data.lbma_key_event}</div>
            <div className="grid grid-cols-2 gap-2">
              {data.lbma_data.map((entry, i) => (
                <div key={i} className="text-sm">
                  <span className="text-gray-400">{entry.metric}:</span>
                  <span className="text-white ml-2">{entry.value}</span>
                  {entry.date && <span className="text-gray-500 text-xs ml-1">({entry.date})</span>}
                </div>
              ))}
            </div>
          </div>
          <div className="text-xs text-gray-500">Sources: {data.lbma_sources.join(', ')}</div>
        </div>

        {/* China Export Restrictions */}
        <div className="mb-4">
          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
            <Globe className="w-4 h-4 text-red-400" /> China Export Restrictions
          </h5>
          <div className="bg-gray-800/50 rounded p-3">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><span className="text-gray-400">Effective:</span> <span className="text-white">{data.china_export_restrictions.effective_date}</span></div>
              <div><span className="text-gray-400">Companies:</span> <span className="text-white">{data.china_export_restrictions.authorized_companies} authorized</span></div>
              <div><span className="text-gray-400">Min Capacity:</span> <span className="text-white">{data.china_export_restrictions.min_capacity}</span></div>
              <div><span className="text-gray-400">Requirement:</span> <span className="text-white">{data.china_export_restrictions.requirement}</span></div>
            </div>
            <div className="text-sm text-red-400 mt-2">{data.china_export_restrictions.impact}</div>
          </div>
        </div>

        {/* Silver Price Action */}
        <div>
          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-400" /> Silver Price Action
          </h5>
          <div className="bg-gray-800/50 rounded p-3">
            <div className="flex gap-4 mb-2">
              <div className="text-sm">
                <span className="text-gray-400">2025:</span> <span className="text-green-400 font-bold">{data.silver_2025_performance}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-400">2026 YTD:</span> <span className="text-green-400 font-bold">{data.silver_2026_ytd}</span>
              </div>
            </div>
            <div className="space-y-1">
              {data.silver_price_action.map((entry, i) => (
                <div key={i} className="flex justify-between text-sm">
                  <span className="text-gray-400">{entry.date}</span>
                  <span className="text-white font-mono">{entry.price}</span>
                  <span className="text-gray-500 text-xs">{entry.event}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* TIER 2: Rumors */}
      <div className="p-4 bg-orange-900/10 rounded-lg border border-orange-500/30">
        <h4 className="font-bold text-orange-400 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" /> TIER 2: Rumors & Unverified Claims
        </h4>
        <div className="space-y-3">
          {data.rumors.map((rumor, i) => (
            <RumorCard key={i} rumor={rumor} />
          ))}
        </div>
      </div>

      {/* TIER 3: Bank Positions */}
      <div className="p-4 bg-blue-900/10 rounded-lg border border-blue-500/30">
        <h4 className="font-bold text-blue-400 mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5" /> TIER 3: Bank Positions & Exposure
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.bank_positions.map((bank, i) => (
            <BankPositionCard key={i} bank={bank} />
          ))}
        </div>
      </div>

      {/* Monitoring Section */}
      <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-400" /> Monitoring & Sources
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Daily Metrics */}
          <div>
            <h5 className="text-sm font-semibold text-cyan-400 mb-2">Daily Metrics</h5>
            <ul className="space-y-1">
              {data.daily_metrics.map((metric, i) => (
                <li key={i} className="text-xs text-gray-400 flex items-center gap-1">
                  <ChevronRight className="w-3 h-3 text-cyan-400" />
                  {metric.name}
                  {metric.source && <span className="text-gray-600">({metric.source})</span>}
                </li>
              ))}
            </ul>
          </div>

          {/* Monthly Metrics */}
          <div>
            <h5 className="text-sm font-semibold text-purple-400 mb-2">Monthly Metrics</h5>
            <ul className="space-y-1">
              {data.monthly_metrics.map((metric, i) => (
                <li key={i} className="text-xs text-gray-400 flex items-center gap-1">
                  <ChevronRight className="w-3 h-3 text-purple-400" />
                  {metric.name}
                  <span className="text-gray-600">({metric.frequency})</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Event Triggers */}
        <div className="mt-4">
          <h5 className="text-sm font-semibold text-orange-400 mb-2">Event Triggers</h5>
          <div className="flex flex-wrap gap-2">
            {data.event_triggers.map((trigger, i) => (
              <span key={i} className="px-2 py-1 bg-orange-900/20 text-orange-400 text-xs rounded">
                {trigger}
              </span>
            ))}
          </div>
        </div>

        {/* Key Sources */}
        <div className="mt-4">
          <h5 className="text-sm font-semibold text-green-400 mb-2">Key Sources</h5>
          <div className="grid grid-cols-3 gap-2">
            {data.key_sources.map((source, i) => (
              <div key={i} className="text-xs">
                <span className="text-gray-500">[{source.category}]</span>{' '}
                {source.url ? (
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                    {source.name} <ExternalLink className="w-3 h-3 inline" />
                  </a>
                ) : (
                  <span className="text-gray-300">{source.name}</span>
                )}
                {source.notes && <span className="text-gray-600 ml-1">({source.notes})</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Search Queries */}
        <div className="mt-4">
          <h5 className="text-sm font-semibold text-gray-400 mb-2">Search Queries</h5>
          <div className="bg-gray-900/50 rounded p-2 max-h-32 overflow-y-auto">
            {data.search_queries.map((query, i) => (
              <div key={i} className="text-xs text-gray-500 font-mono py-0.5">
                {query}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
