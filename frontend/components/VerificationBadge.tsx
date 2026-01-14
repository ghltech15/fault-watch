'use client'

interface VerificationBadgeProps {
  status: 'verified' | 'partial' | 'theory' | 'unverified' | string
  sourceCount?: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const configs: Record<string, { label: string; color: string; icon: string }> = {
  verified: {
    label: 'VERIFIED',
    color: 'bg-green-500/20 text-green-400 border-green-500/50',
    icon: '✓'
  },
  partial: {
    label: 'SOURCES',
    color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    icon: '◐'
  },
  theory: {
    label: 'WORKING THEORY',
    color: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    icon: '?'
  },
  unverified: {
    label: 'UNVERIFIED',
    color: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
    icon: '○'
  }
}

const sizeClasses = {
  sm: 'px-1.5 py-0.5 text-[10px]',
  md: 'px-2 py-0.5 text-xs',
  lg: 'px-2.5 py-1 text-sm'
}

export function VerificationBadge({
  status,
  sourceCount = 0,
  showLabel = true,
  size = 'md'
}: VerificationBadgeProps) {
  const config = configs[status] || configs.unverified

  // For partial status, show source count
  const label = status === 'partial' && sourceCount > 0
    ? `${sourceCount} ${config.label}`
    : config.label

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded border font-medium
        ${config.color}
        ${sizeClasses[size]}
      `}
    >
      <span>{config.icon}</span>
      {showLabel && <span>{label}</span>}
    </span>
  )
}

// Simple status dot for compact display
export function VerificationDot({
  status
}: {
  status: 'verified' | 'partial' | 'theory' | 'unverified' | string
}) {
  const colors: Record<string, string> = {
    verified: 'bg-green-500',
    partial: 'bg-yellow-500',
    theory: 'bg-orange-500',
    unverified: 'bg-gray-500'
  }

  return (
    <span
      className={`inline-block w-2 h-2 rounded-full ${colors[status] || colors.unverified}`}
      title={status.charAt(0).toUpperCase() + status.slice(1)}
    />
  )
}
