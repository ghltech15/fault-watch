'use client'

import { TrendingUp, TrendingDown, AlertTriangle, Package, Truck, Globe } from 'lucide-react'
import { SilverMarket, getVerificationColor, formatOunces } from '@/lib/crisis-scanner-types'
import { VerificationBadge } from '@/components/VerificationBadge'

interface SilverIndicatorsProps {
  silver: SilverMarket
}

export function SilverIndicators({ silver }: SilverIndicatorsProps) {
  const { price_data, market_structure, comex_inventory, delivery_activity, supply_deficit, china_export_curbs, physical_premium_reports } = silver

  return (
    <div className="scanner-card">
      <div className="scanner-card-header">
        <div className="flex items-center gap-2">
          <div className="scanner-icon-box">
            <TrendingUp className="w-4 h-4" />
          </div>
          <h3 className="scanner-card-title">SILVER MARKET INDICATORS</h3>
        </div>
        <VerificationBadge status={market_structure.verification.toLowerCase()} size="xs" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Price Section */}
        <div className="scanner-stat-box">
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Spot Price</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-amber-400 tabular-nums">
              ${price_data.spot_price.toFixed(2)}
            </span>
          </div>
          <div className="mt-2 grid grid-cols-2 gap-2 text-[10px]">
            <div>
              <span className="text-gray-600">High: </span>
              <span className="text-emerald-400">${price_data.user_tracked_high}</span>
            </div>
            <div>
              <span className="text-gray-600">Low: </span>
              <span className="text-red-400">${price_data.user_tracked_low}</span>
            </div>
          </div>
          <div className="mt-1 text-[9px] text-gray-600 italic">
            {price_data.user_thesis}
          </div>
        </div>

        {/* Market Structure */}
        <div className={`scanner-stat-box ${market_structure.backwardation ? 'border-red-500/50' : 'border-emerald-500/50'}`}>
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Market Structure</div>
          <div className="flex items-center gap-2">
            {market_structure.backwardation ? (
              <>
                <AlertTriangle className="w-5 h-5 text-red-500 animate-pulse" />
                <span className="text-lg font-bold text-red-400">BACKWARDATION</span>
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                <span className="text-lg font-bold text-emerald-400">CONTANGO</span>
              </>
            )}
          </div>
          <div className="mt-2 text-[10px] text-gray-400">
            Status: <span className={market_structure.backwardation ? 'text-red-400' : 'text-emerald-400'}>
              {market_structure.backwardation_status}
            </span>
          </div>
          <div className="mt-1 text-[9px] text-gray-600">
            {market_structure.significance}
          </div>
          <div className="mt-1 text-[9px] text-gray-700">
            Source: {market_structure.source}
          </div>
        </div>
      </div>

      {/* COMEX Inventory & Deliveries */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="scanner-stat-box">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-[10px] uppercase tracking-wider text-gray-500">COMEX Registered</span>
            <VerificationBadge status="verified" size="xs" showLabel={false} />
          </div>
          <div className="text-xl font-bold text-white tabular-nums">
            {formatOunces(comex_inventory.registered_oz)}
          </div>
          <div className="flex items-center gap-1 mt-1">
            <TrendingDown className="w-3 h-3 text-red-400" />
            <span className="text-[10px] text-red-400 font-medium">{comex_inventory.trend}</span>
          </div>
          <div className="text-[9px] text-gray-600 mt-1">
            {comex_inventory.registered_tons.toLocaleString()} tons | As of {comex_inventory.as_of_date}
          </div>
        </div>

        <div className="scanner-stat-box">
          <div className="flex items-center gap-2 mb-2">
            <Truck className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-[10px] uppercase tracking-wider text-gray-500">Delivery Activity</span>
            <VerificationBadge status="verified" size="xs" showLabel={false} />
          </div>
          <div className="text-xl font-bold text-white tabular-nums">
            {formatOunces(delivery_activity.ounces_delivered)}
          </div>
          <div className="text-[10px] text-gray-400 mt-1">
            {delivery_activity.contracts_delivered.toLocaleString()} contracts
          </div>
          <div className="text-[10px] text-amber-400 mt-1">
            {delivery_activity.primary_issuer}: {delivery_activity.issuer_percentage}% of issuance
          </div>
        </div>
      </div>

      {/* Supply Deficit & China Curbs */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="scanner-stat-box border-orange-500/30">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
            <span className="text-[10px] uppercase tracking-wider text-gray-500">Supply Deficit</span>
            <VerificationBadge status="verified" size="xs" showLabel={false} />
          </div>
          <div className="text-lg font-bold text-orange-400 tabular-nums">
            {formatOunces(supply_deficit.deficit_oz)}
          </div>
          <div className="text-[10px] text-gray-400 mt-1">
            {supply_deficit.consecutive_deficit_years} consecutive years of deficit
          </div>
          <div className="text-[10px] text-gray-500 mt-1">
            2026 projected: {formatOunces(supply_deficit.projected_2026_deficit_oz)}
          </div>
        </div>

        <div className="scanner-stat-box border-red-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Globe className="w-3.5 h-3.5 text-red-400" />
            <span className="text-[10px] uppercase tracking-wider text-gray-500">China Export Curbs</span>
            <VerificationBadge status="verified" size="xs" showLabel={false} />
          </div>
          <div className="text-sm font-bold text-red-400">
            65% SUPPLY RING-FENCED
          </div>
          <div className="text-[10px] text-gray-400 mt-1">
            Effective: {china_export_curbs.effective_date}
          </div>
          <div className="text-[9px] text-gray-600 mt-1 line-clamp-2">
            {china_export_curbs.impact_description}
          </div>
        </div>
      </div>

      {/* Physical Premium Reports */}
      <div className="mt-4 p-3 bg-orange-500/5 border border-orange-500/20 rounded">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] uppercase tracking-wider text-orange-400 font-bold">Physical Premium Reports</span>
          <VerificationBadge status="unverified" size="xs" />
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Tokyo: </span>
            <span className="text-orange-300">${physical_premium_reports.tokyo_premium_claimed}/oz claimed</span>
          </div>
          <div>
            <span className="text-gray-500">Dubai: </span>
            <span className="text-orange-300">{physical_premium_reports.dubai_premium_claimed}</span>
          </div>
        </div>
        <div className="text-[9px] text-gray-600 mt-2 italic">
          {physical_premium_reports.note}
        </div>
      </div>
    </div>
  )
}
