'use client'

import { AlertTriangle, CheckCircle, FileText, HelpCircle, MessageSquare, ExternalLink } from 'lucide-react'

// Comprehensive verification status types
export type VerificationStatus =
  | 'verified'      // Confirmed by official sources (SEC filings, exchange data)
  | 'official'      // From regulatory/official documents
  | 'calculated'    // Derived from verified data points
  | 'reported'      // Reported by credible news sources
  | 'rumored'       // Market rumors, unconfirmed
  | 'theory'        // Analytical hypothesis
  | 'estimated'     // Best estimate based on available data
  | 'unverified'    // No source confirmation

interface VerificationBadgeProps {
  status: VerificationStatus | string
  sourceCount?: number
  source?: string
  sourceUrl?: string
  showLabel?: boolean
  size?: 'xs' | 'sm' | 'md' | 'lg'
  showTooltip?: boolean
}

const configs: Record<string, {
  label: string
  shortLabel: string
  color: string
  bgColor: string
  borderColor: string
  icon: any
  description: string
}> = {
  verified: {
    label: 'VERIFIED',
    shortLabel: 'V',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/40',
    icon: CheckCircle,
    description: 'Confirmed by official sources'
  },
  official: {
    label: 'OFFICIAL',
    shortLabel: 'O',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/40',
    icon: FileText,
    description: 'From regulatory filings'
  },
  calculated: {
    label: 'CALCULATED',
    shortLabel: 'C',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/40',
    icon: CheckCircle,
    description: 'Derived from verified data'
  },
  reported: {
    label: 'REPORTED',
    shortLabel: 'R',
    color: 'text-sky-400',
    bgColor: 'bg-sky-500/10',
    borderColor: 'border-sky-500/40',
    icon: MessageSquare,
    description: 'Credible news source'
  },
  estimated: {
    label: 'ESTIMATED',
    shortLabel: 'E',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/40',
    icon: HelpCircle,
    description: 'Best estimate from data'
  },
  rumored: {
    label: 'RUMORED',
    shortLabel: '!',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/40',
    icon: AlertTriangle,
    description: 'Unconfirmed market rumor'
  },
  theory: {
    label: 'THEORY',
    shortLabel: 'T',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/40',
    icon: HelpCircle,
    description: 'Analytical hypothesis'
  },
  partial: {
    label: 'PARTIAL',
    shortLabel: 'P',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/40',
    icon: HelpCircle,
    description: 'Partially verified'
  },
  unverified: {
    label: 'UNVERIFIED',
    shortLabel: '?',
    color: 'text-gray-500',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/40',
    icon: HelpCircle,
    description: 'No source confirmation'
  }
}

const sizeClasses = {
  xs: 'px-1 py-0.5 text-[9px] gap-0.5',
  sm: 'px-1.5 py-0.5 text-[10px] gap-1',
  md: 'px-2 py-1 text-xs gap-1',
  lg: 'px-2.5 py-1 text-sm gap-1.5'
}

const iconSizes = {
  xs: 'w-2.5 h-2.5',
  sm: 'w-3 h-3',
  md: 'w-3.5 h-3.5',
  lg: 'w-4 h-4'
}

export function VerificationBadge({
  status,
  sourceCount = 0,
  source,
  sourceUrl,
  showLabel = true,
  size = 'sm'
}: VerificationBadgeProps) {
  const config = configs[status] || configs.unverified
  const Icon = config.icon

  const label = status === 'partial' && sourceCount > 0
    ? `${sourceCount} SOURCES`
    : config.label

  return (
    <span
      className={`
        inline-flex items-center rounded font-bold uppercase tracking-wider border
        ${config.bgColor} ${config.color} ${config.borderColor}
        ${sizeClasses[size]}
      `}
      title={`${config.description}${source ? ` - Source: ${source}` : ''}`}
    >
      <Icon className={iconSizes[size]} />
      {showLabel && <span>{label}</span>}
      {sourceUrl && (
        <ExternalLink className={`${iconSizes[size]} opacity-60`} />
      )}
    </span>
  )
}

// Compact dot indicator for tight spaces
export function VerificationDot({
  status,
  size = 'md'
}: {
  status: VerificationStatus | string
  size?: 'sm' | 'md' | 'lg'
}) {
  const config = configs[status] || configs.unverified
  const sizes = { sm: 'w-1.5 h-1.5', md: 'w-2 h-2', lg: 'w-2.5 h-2.5' }

  return (
    <span
      className={`inline-block rounded-full ${sizes[size]} ${config.color.replace('text-', 'bg-')}`}
      title={config.description}
    />
  )
}

// Data point with inline verification
export function VerifiedDataPoint({
  label,
  value,
  unit,
  status,
  source,
  sourceUrl,
  trend,
  size = 'md'
}: {
  label: string
  value: string | number
  unit?: string
  status: VerificationStatus
  source?: string
  sourceUrl?: string
  trend?: 'up' | 'down' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
}) {
  const config = configs[status] || configs.unverified
  const trendColors = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-gray-400'
  }

  const valueSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl'
  }

  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] uppercase tracking-wider text-gray-500">{label}</span>
        <VerificationBadge status={status} size="xs" source={source} sourceUrl={sourceUrl} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`font-bold ${valueSizes[size]} ${trend ? trendColors[trend] : 'text-white'}`}>
          {value}
        </span>
        {unit && <span className="text-gray-500 text-sm">{unit}</span>}
      </div>
      {source && (
        <div className="text-[9px] text-gray-600 mt-0.5">
          Source: {sourceUrl ? (
            <a href={sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-400">
              {source}
            </a>
          ) : source}
        </div>
      )}
    </div>
  )
}

// Card header with verification status
export function CardHeader({
  title,
  status,
  source,
  lastUpdated,
  icon: Icon
}: {
  title: string
  status: VerificationStatus
  source?: string
  lastUpdated?: string
  icon?: any
}) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-gray-500" />}
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">{title}</h3>
      </div>
      <div className="flex items-center gap-2">
        <VerificationBadge status={status} source={source} size="xs" />
        {lastUpdated && (
          <span className="text-[9px] text-gray-600">{lastUpdated}</span>
        )}
      </div>
    </div>
  )
}

// Legend component showing all verification types
export function VerificationLegend({ compact = false }: { compact?: boolean }) {
  const statuses: VerificationStatus[] = ['verified', 'official', 'calculated', 'reported', 'estimated', 'rumored', 'theory']

  if (compact) {
    return (
      <div className="flex items-center gap-3 text-[9px]">
        {statuses.map(status => {
          const config = configs[status]
          return (
            <span key={status} className={`flex items-center gap-1 ${config.color}`}>
              <VerificationDot status={status} size="sm" />
              {config.shortLabel}
            </span>
          )
        })}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 p-3 bg-black/30 rounded-lg text-[10px]">
      {statuses.map(status => {
        const config = configs[status]
        const Icon = config.icon
        return (
          <div key={status} className={`flex items-center gap-1.5 ${config.color}`}>
            <Icon className="w-3 h-3" />
            <span className="font-bold">{config.label}</span>
            <span className="text-gray-600">- {config.description}</span>
          </div>
        )
      })}
    </div>
  )
}
