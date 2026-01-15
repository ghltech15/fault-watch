'use client'

import { Building2, AlertCircle, TrendingDown, Check, Clock } from 'lucide-react'
import { FederalReserve, formatLargeNumber } from '@/lib/crisis-scanner-types'
import { VerificationBadge } from '@/components/VerificationBadge'

interface FedFacilitiesProps {
  fed: FederalReserve
}

export function FedFacilities({ fed }: FedFacilitiesProps) {
  const { standing_repo_facility, year_end_spike, reverse_repo, quantitative_tightening } = fed

  return (
    <div className="scanner-card">
      <div className="scanner-card-header">
        <div className="flex items-center gap-2">
          <div className="scanner-icon-box">
            <Building2 className="w-4 h-4" />
          </div>
          <h3 className="scanner-card-title">FED FACILITIES</h3>
        </div>
        <VerificationBadge status="verified" size="xs" />
      </div>

      {/* Standing Repo Facility */}
      <div className="scanner-stat-box mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] uppercase tracking-wider text-gray-500">Standing Repo Facility (SRF)</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
            standing_repo_facility.current_balance === 0
              ? 'bg-emerald-500/20 text-emerald-400'
              : 'bg-red-500/20 text-red-400'
          }`}>
            {standing_repo_facility.current_balance === 0 ? 'INACTIVE' : 'ACTIVE'}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Current Balance</div>
            <div className="text-2xl font-black text-white tabular-nums">
              {standing_repo_facility.current_balance === 0 ? '$0' : formatLargeNumber(standing_repo_facility.current_balance)}
            </div>
          </div>
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Daily Limit</div>
            <div className="text-xl font-bold text-red-400">
              {standing_repo_facility.daily_limit}
            </div>
            <div className="text-[9px] text-gray-600">
              Changed: {standing_repo_facility.limit_change_date}
            </div>
          </div>
        </div>

        <div className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded text-[10px]">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <span className="text-red-400 font-bold">Policy Alert: </span>
              <span className="text-gray-400">{standing_repo_facility.significance}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Year-End Spike Event */}
      <div className={`scanner-stat-box mb-4 ${year_end_spike.status === 'RESOLVED' ? 'border-emerald-500/30' : 'border-red-500/50'}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] uppercase tracking-wider text-gray-500">Year-End Liquidity Spike</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1 ${
            year_end_spike.status === 'RESOLVED'
              ? 'bg-emerald-500/20 text-emerald-400'
              : 'bg-red-500/20 text-red-400'
          }`}>
            {year_end_spike.status === 'RESOLVED' ? (
              <><Check className="w-3 h-3" /> RESOLVED</>
            ) : (
              <><AlertCircle className="w-3 h-3" /> ACTIVE</>
            )}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Peak Amount</div>
            <div className="text-lg font-bold text-amber-400 tabular-nums">
              {formatLargeNumber(year_end_spike.amount)}
            </div>
            <div className="text-[9px] text-gray-600">{year_end_spike.date}</div>
          </div>
          <div>
            <div className="text-[9px] text-gray-600 mb-1">Treasury</div>
            <div className="text-sm font-bold text-white tabular-nums">
              {formatLargeNumber(year_end_spike.treasury_collateral)}
            </div>
          </div>
          <div>
            <div className="text-[9px] text-gray-600 mb-1">MBS</div>
            <div className="text-sm font-bold text-white tabular-nums">
              {formatLargeNumber(year_end_spike.mbs_collateral)}
            </div>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-[10px]">
          <span className="text-gray-500">Previous record: {formatLargeNumber(year_end_spike.previous_record)}</span>
          {year_end_spike.resolution_date && (
            <span className="text-emerald-400">
              <Clock className="w-3 h-3 inline mr-1" />
              Resolved: {year_end_spike.resolution_date}
            </span>
          )}
        </div>

        <div className="mt-2 text-[9px] text-gray-600 italic">
          {year_end_spike.significance}
        </div>
      </div>

      {/* Reverse Repo & QT */}
      <div className="grid grid-cols-2 gap-4">
        <div className="scanner-stat-box">
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Reverse Repo (ON RRP)</div>
          <div className="text-xl font-bold text-white tabular-nums">
            {formatLargeNumber(reverse_repo.current_balance)}
          </div>
          <div className="text-[9px] text-gray-600 mt-1">
            Year-end spike: {formatLargeNumber(reverse_repo.year_end_spike)}
          </div>
        </div>

        <div className="scanner-stat-box">
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">Quantitative Tightening</div>
          <div className={`text-lg font-bold ${quantitative_tightening.status === 'ENDED' ? 'text-emerald-400' : 'text-red-400'}`}>
            {quantitative_tightening.status}
          </div>
          <div className="text-[9px] text-gray-600 mt-1">
            Total reduction: {formatLargeNumber(quantitative_tightening.total_reduction)}
          </div>
          {quantitative_tightening.end_date && (
            <div className="text-[9px] text-gray-600">
              Ended: {quantitative_tightening.end_date}
            </div>
          )}
        </div>
      </div>

      {/* Source Attribution */}
      <div className="mt-4 text-[9px] text-gray-700 flex items-center gap-2">
        <VerificationBadge status="verified" size="xs" showLabel={false} />
        <span>Sources: Federal Reserve FOMC, NY Fed Daily Operations</span>
      </div>
    </div>
  )
}
