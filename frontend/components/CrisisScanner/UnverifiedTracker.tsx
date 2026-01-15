'use client'

import { AlertTriangle, Eye, XCircle, CheckCircle, HelpCircle, ExternalLink } from 'lucide-react'
import { UnverifiedClaim, getVerificationColor } from '@/lib/crisis-scanner-types'
import { VerificationBadge } from '@/components/VerificationBadge'

interface UnverifiedTrackerProps {
  claims: UnverifiedClaim[]
}

function ClaimStatusBadge({ status }: { status: string }) {
  const configs: Record<string, { color: string; bg: string; icon: any; label: string }> = {
    'UNVERIFIED': {
      color: 'text-orange-400',
      bg: 'bg-orange-500/20 border-orange-500/40',
      icon: Eye,
      label: 'AWAITING CORROBORATION'
    },
    'SPECULATIVE': {
      color: 'text-red-400',
      bg: 'bg-red-500/20 border-red-500/40',
      icon: XCircle,
      label: 'SPECULATIVE'
    },
    'EFFECTIVELY_DEBUNKED': {
      color: 'text-gray-400',
      bg: 'bg-gray-500/20 border-gray-500/40',
      icon: XCircle,
      label: 'DEBUNKED'
    },
    'PARTIALLY_CORROBORATED': {
      color: 'text-amber-400',
      bg: 'bg-amber-500/20 border-amber-500/40',
      icon: HelpCircle,
      label: 'PARTIALLY CORROBORATED'
    },
    'CREDIBLE_ALLEGATION': {
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/20 border-yellow-500/40',
      icon: Eye,
      label: 'CREDIBLE - MONITORING'
    },
    'CONFIRMED': {
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/20 border-emerald-500/40',
      icon: CheckCircle,
      label: 'CONFIRMED'
    }
  }

  const config = configs[status] || configs['UNVERIFIED']
  const Icon = config.icon

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-[9px] font-bold border ${config.bg} ${config.color}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

function ClaimCard({ claim }: { claim: UnverifiedClaim }) {
  const isDebunked = claim.status === 'EFFECTIVELY_DEBUNKED' || claim.verification_status === 'SPECULATIVE'

  return (
    <div className={`p-3 rounded-lg border ${
      isDebunked
        ? 'bg-gray-900/30 border-gray-800 opacity-60'
        : 'bg-black/40 border-gray-700'
    }`}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex-1">
          <div className="text-sm font-medium text-white">{claim.claim}</div>
          {claim.exposure_claimed && (
            <div className="text-[10px] text-amber-400 mt-1">
              Exposure claimed: {claim.exposure_claimed}
            </div>
          )}
        </div>
        <ClaimStatusBadge status={claim.verification_status as string} />
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] mb-2">
        <div>
          <span className="text-gray-600">Source: </span>
          <span className="text-gray-400">{claim.source}</span>
        </div>
        <div>
          <span className="text-gray-600">Type: </span>
          <span className="text-gray-400">{claim.source_type}</span>
        </div>
        {claim.author && (
          <div className="col-span-2">
            <span className="text-gray-600">Author: </span>
            <span className="text-gray-400">{claim.author}</span>
          </div>
        )}
        {claim.date_reported && (
          <div>
            <span className="text-gray-600">Reported: </span>
            <span className="text-gray-400">{claim.date_reported}</span>
          </div>
        )}
      </div>

      {/* Concerns / Debunked By */}
      {claim.credibility_concerns && claim.credibility_concerns.length > 0 && (
        <div className="mt-2 p-2 bg-orange-500/5 border border-orange-500/20 rounded text-[9px]">
          <div className="text-orange-400 font-bold mb-1 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Credibility Concerns
          </div>
          <ul className="text-gray-500 space-y-0.5 ml-4 list-disc">
            {claim.credibility_concerns.map((concern, i) => (
              <li key={i}>{concern}</li>
            ))}
          </ul>
        </div>
      )}

      {claim.debunked_by && claim.debunked_by.length > 0 && (
        <div className="mt-2 p-2 bg-gray-500/5 border border-gray-500/20 rounded text-[9px]">
          <div className="text-gray-400 font-bold mb-1 flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            Debunked By
          </div>
          <ul className="text-gray-600 space-y-0.5 ml-4 list-disc">
            {claim.debunked_by.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {claim.notes && (
        <div className="mt-2 text-[9px] text-gray-500 italic">{claim.notes}</div>
      )}

      {/* Recommended Action */}
      <div className="mt-3 pt-2 border-t border-gray-800 text-[10px]">
        <span className="text-gray-600">Action: </span>
        <span className="text-gray-400">{claim.recommended_action}</span>
      </div>

      {claim.escalation_trigger && (
        <div className="mt-1 text-[9px] text-amber-500/70">
          <span className="font-bold">Escalation trigger: </span>
          {claim.escalation_trigger}
        </div>
      )}
    </div>
  )
}

export function UnverifiedTracker({ claims }: UnverifiedTrackerProps) {
  // Sort: active claims first, debunked last
  const sortedClaims = [...claims].sort((a, b) => {
    const aDebunked = a.status === 'EFFECTIVELY_DEBUNKED' ? 1 : 0
    const bDebunked = b.status === 'EFFECTIVELY_DEBUNKED' ? 1 : 0
    return aDebunked - bDebunked
  })

  const activeClaims = claims.filter(c => c.status !== 'EFFECTIVELY_DEBUNKED')
  const debunkedClaims = claims.filter(c => c.status === 'EFFECTIVELY_DEBUNKED')

  return (
    <div className="scanner-card border-orange-500/30">
      <div className="scanner-card-header">
        <div className="flex items-center gap-2">
          <div className="scanner-icon-box bg-orange-500/20">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
          </div>
          <h3 className="scanner-card-title">UNVERIFIED CLAIMS TRACKER</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2 py-1 rounded bg-orange-500/20 text-orange-400 font-bold">
            {activeClaims.length} ACTIVE
          </span>
          {debunkedClaims.length > 0 && (
            <span className="text-[10px] px-2 py-1 rounded bg-gray-500/20 text-gray-400 font-bold">
              {debunkedClaims.length} DEBUNKED
            </span>
          )}
        </div>
      </div>

      {/* Warning Banner */}
      <div className="mb-4 p-2 bg-orange-500/10 border border-orange-500/30 rounded flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0" />
        <span className="text-[10px] text-orange-300">
          <strong>CAUTION:</strong> Claims below are unverified and should not be treated as fact.
          Monitor for corroboration from official sources.
        </span>
      </div>

      {/* Claims List */}
      <div className="space-y-3">
        {sortedClaims.map((claim) => (
          <ClaimCard key={claim.id} claim={claim} />
        ))}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-gray-800">
        <div className="text-[9px] uppercase tracking-wider text-gray-600 mb-2">Verification Status Guide</div>
        <div className="flex flex-wrap gap-2 text-[9px]">
          <span className="px-2 py-1 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
            AWAITING = Monitor
          </span>
          <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
            PARTIAL = Some evidence
          </span>
          <span className="px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/30">
            SPECULATIVE = Unsubstantiated
          </span>
          <span className="px-2 py-1 rounded bg-gray-500/10 text-gray-400 border border-gray-500/30">
            DEBUNKED = Disproven
          </span>
        </div>
      </div>
    </div>
  )
}
