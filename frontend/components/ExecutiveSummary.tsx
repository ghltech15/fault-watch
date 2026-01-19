'use client'

import { useQuery } from '@tanstack/react-query'
import { api, CrisisGaugeData, DashboardData } from '@/lib/api'
import { VerificationBadge, VerificationLegend, VerifiedDataPoint } from './VerificationBadge'
import { motion } from 'framer-motion'
import {
  AlertTriangle, TrendingUp, TrendingDown, Clock, Building2,
  Activity, Target, Zap, Shield, Eye, Radio
} from 'lucide-react'

interface ExecutiveSummaryProps {
  dashboard: DashboardData
}

// Market status indicator
function MarketStatus() {
  const now = new Date()
  const hour = now.getUTCHours()
  const day = now.getUTCDay()
  const isWeekend = day === 0 || day === 6
  const isMarketHours = hour >= 13 && hour < 21 // 9:30 AM - 4 PM ET in UTC

  const isOpen = !isWeekend && isMarketHours

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold ${
      isOpen ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'
    }`}>
      <span className={`w-2 h-2 rounded-full ${isOpen ? 'bg-emerald-400 animate-pulse' : 'bg-gray-500'}`} />
      {isOpen ? 'MARKETS OPEN' : 'MARKETS CLOSED'}
    </div>
  )
}

// Quick status pill
function StatusPill({
  label,
  value,
  status,
  trend
}: {
  label: string
  value: string
  status: 'good' | 'warning' | 'danger' | 'neutral'
  trend?: 'up' | 'down'
}) {
  const colors = {
    good: 'border-emerald-500/40 bg-emerald-500/10',
    warning: 'border-amber-500/40 bg-amber-500/10',
    danger: 'border-red-500/40 bg-red-500/10',
    neutral: 'border-gray-500/40 bg-gray-500/10'
  }

  const textColors = {
    good: 'text-emerald-400',
    warning: 'text-amber-400',
    danger: 'text-red-400',
    neutral: 'text-gray-400'
  }

  return (
    <div className={`px-3 py-2 rounded-lg border ${colors[status]}`}>
      <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-0.5">{label}</div>
      <div className={`text-lg font-bold ${textColors[status]} flex items-center gap-1`}>
        {value}
        {trend === 'up' && <TrendingUp className="w-3 h-3" />}
        {trend === 'down' && <TrendingDown className="w-3 h-3" />}
      </div>
    </div>
  )
}

export function ExecutiveSummary({ dashboard }: ExecutiveSummaryProps) {
  const { data: crisisData } = useQuery({
    queryKey: ['crisis-gauge'],
    queryFn: api.getCrisisGauge,
    refetchInterval: 30000
  })
  const { data: nakedShorts } = useQuery({
    queryKey: ['naked-shorts'],
    queryFn: api.getNakedShorts,
    refetchInterval: 60000
  })

  const silver = dashboard.prices.silver || { price: 0, change_pct: 0 }
  const gold = dashboard.prices.gold || { price: 0, change_pct: 0 }

  // Calculate key metrics
  const silverMove = crisisData ? crisisData.silver_move : silver.price - 30
  const totalLoss = crisisData ? crisisData.losses.reduce((sum, l) => sum + l.total_loss, 0) : 0
  const verifiedLoss = crisisData ? crisisData.losses.filter(l => l.is_verified).reduce((sum, l) => sum + l.total_loss, 0) : 0
  const cracksShowing = crisisData ? crisisData.cracks_showing_count : 0
  const totalCracks = crisisData ? crisisData.total_cracks : 15
  const currentPhase = crisisData ? crisisData.current_phase : 1
  const crisisLevel = crisisData ? crisisData.crisis_level : 'Hidden Stress'
  const crisisProbability = crisisData ? crisisData.crisis_probability : 0

  // Determine overall status
  const overallStatus =
    crisisProbability >= 70 ? 'danger' :
    crisisProbability >= 40 ? 'warning' :
    'good'

  return (
    <div className="bg-black/40 border-b border-gray-800">
      {/* Top Bar - Market Status & Timestamps */}
      <div className="border-b border-gray-800/50 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <MarketStatus />
            <span className="text-[10px] text-gray-600">
              Data as of {new Date(dashboard.last_updated).toLocaleString()}
            </span>
          </div>
          <VerificationLegend compact />
        </div>
      </div>

      {/* Main Summary Grid */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">

          {/* LEFT: Key Metrics (4 cols) */}
          <div className="col-span-12 lg:col-span-4 space-y-4">
            <h2 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold flex items-center gap-2">
              <Eye className="w-3 h-3" /> KEY METRICS
            </h2>

            <div className="grid grid-cols-2 gap-3">
              {/* Silver Price - VERIFIED */}
              <div className="p-3 rounded-lg bg-black/30 border border-gray-800">
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-[9px] uppercase text-gray-500">Silver Spot</span>
                  <VerificationBadge status="verified" size="xs" source="COMEX" />
                </div>
                <div className={`text-2xl font-black ${silver.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  ${silver.price.toFixed(2)}
                </div>
                <div className={`text-xs ${silver.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {silver.change_pct >= 0 ? '+' : ''}{silver.change_pct.toFixed(2)}%
                </div>
              </div>

              {/* Silver Move - CALCULATED */}
              <div className="p-3 rounded-lg bg-black/30 border border-gray-800">
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-[9px] uppercase text-gray-500">Move from $30</span>
                  <VerificationBadge status="calculated" size="xs" />
                </div>
                <div className="text-2xl font-black text-red-400">
                  +${silverMove.toFixed(2)}
                </div>
                <div className="text-[9px] text-gray-500">
                  Base: $30/oz
                </div>
              </div>

              {/* COMEX Loss - VERIFIED */}
              <div className="p-3 rounded-lg bg-black/30 border border-emerald-500/20">
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-[9px] uppercase text-gray-500">COMEX Loss</span>
                  <VerificationBadge status="verified" size="xs" source="CME" />
                </div>
                <div className="text-xl font-black text-red-400">
                  ${(verifiedLoss / 1e9).toFixed(1)}B
                </div>
                <div className="text-[9px] text-emerald-400">
                  212M oz registered
                </div>
              </div>

              {/* Bank Losses - RUMORED */}
              <div className="p-3 rounded-lg bg-black/30 border border-orange-500/20">
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-[9px] uppercase text-gray-500">Est. Bank Losses</span>
                  <VerificationBadge status="rumored" size="xs" />
                </div>
                <div className="text-xl font-black text-orange-400">
                  ${((totalLoss - verifiedLoss) / 1e9).toFixed(0)}B
                </div>
                <div className="text-[9px] text-orange-400">
                  Unconfirmed positions
                </div>
              </div>
            </div>

            {/* Paper to Physical */}
            {nakedShorts && (
              <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] uppercase text-gray-500">Paper to Physical Ratio</span>
                  <VerificationBadge status="calculated" size="xs" source="OCC/CME" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-red-400">{nakedShorts.paper_to_physical_ratio}:1</span>
                  <span className="text-xs text-gray-500">short exposure vs available</span>
                </div>
              </div>
            )}
          </div>

          {/* CENTER: Crisis Status (4 cols) */}
          <div className="col-span-12 lg:col-span-4">
            <h2 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold flex items-center gap-2 mb-4">
              <Activity className="w-3 h-3" /> CRISIS STATUS
            </h2>

            {/* Crisis Gauge */}
            <div className="relative flex justify-center mb-4">
              <svg width="180" height="180" viewBox="0 0 180 180" className="drop-shadow-lg">
                {/* Background ring */}
                <circle cx="90" cy="90" r="70" fill="none" stroke="#1a1a1a" strokeWidth="14" />
                {/* Progress ring */}
                <circle
                  cx="90" cy="90" r="70"
                  fill="none"
                  stroke={crisisData?.crisis_color || '#fbbf24'}
                  strokeWidth="14"
                  strokeLinecap="round"
                  strokeDasharray={`${crisisProbability * 4.4} 440`}
                  transform="rotate(-90 90 90)"
                  className="transition-all duration-1000"
                  style={{ filter: `drop-shadow(0 0 8px ${crisisData?.crisis_color || '#fbbf24'})` }}
                />
                {/* Center content */}
                <text x="90" y="80" textAnchor="middle" className="fill-white text-3xl font-black">
                  {crisisProbability.toFixed(0)}%
                </text>
                <text x="90" y="100" textAnchor="middle" className="fill-gray-500 text-[10px] uppercase">
                  Crisis Risk
                </text>
              </svg>
            </div>

            {/* Phase & Level */}
            <div className="text-center mb-4">
              <span
                className="inline-block px-4 py-2 rounded-full text-sm font-bold"
                style={{
                  backgroundColor: `${crisisData?.crisis_color || '#fbbf24'}20`,
                  color: crisisData?.crisis_color || '#fbbf24',
                  border: `1px solid ${crisisData?.crisis_color || '#fbbf24'}40`
                }}
              >
                Phase {currentPhase}: {crisisLevel}
              </span>
            </div>

            {/* Crack Indicators */}
            <div className="p-3 rounded-lg bg-black/30 border border-gray-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] uppercase text-gray-500">System Cracks Detected</span>
                <VerificationBadge status="calculated" size="xs" />
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-2xl font-black ${cracksShowing > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {cracksShowing} / {totalCracks}
                </span>
                <div className="flex-1">
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full transition-all duration-500"
                      style={{ width: `${(cracksShowing / totalCracks) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: Quick Status & Deadlines (4 cols) */}
          <div className="col-span-12 lg:col-span-4 space-y-4">
            <h2 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold flex items-center gap-2">
              <Radio className="w-3 h-3" /> STATUS OVERVIEW
            </h2>

            {/* Quick Status Grid */}
            <div className="grid grid-cols-2 gap-2">
              <StatusPill
                label="Risk Index"
                value={dashboard.risk_index.toFixed(1)}
                status={dashboard.risk_index >= 7 ? 'danger' : dashboard.risk_index >= 4 ? 'warning' : 'good'}
              />
              <StatusPill
                label="Cascade Stage"
                value={`${currentPhase} of 5`}
                status={currentPhase >= 4 ? 'danger' : currentPhase >= 2 ? 'warning' : 'good'}
              />
              <StatusPill
                label="Gold"
                value={`$${gold.price.toFixed(0)}`}
                status={gold.change_pct >= 2 ? 'warning' : 'neutral'}
                trend={gold.change_pct >= 0 ? 'up' : 'down'}
              />
              <StatusPill
                label="VIX"
                value={(dashboard.prices.vix?.price || 0).toFixed(1)}
                status={(dashboard.prices.vix?.price || 0) >= 30 ? 'danger' : (dashboard.prices.vix?.price || 0) >= 20 ? 'warning' : 'good'}
              />
            </div>

            {/* Critical Deadlines */}
            <div className="space-y-2">
              <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-bold flex items-center gap-2">
                <Clock className="w-3 h-3" /> CRITICAL DEADLINES
              </h3>

              <div className={`p-3 rounded-lg border ${
                dashboard.countdowns.lloyds.days < 30 ? 'border-red-500/40 bg-red-500/5' : 'border-gray-800 bg-black/30'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase text-gray-500">Lloyd's Delivery</span>
                    <VerificationBadge status="official" size="xs" source="Lloyd's" />
                  </div>
                  <span className={`text-lg font-bold ${dashboard.countdowns.lloyds.days < 30 ? 'text-red-400' : 'text-white'}`}>
                    {dashboard.countdowns.lloyds.days}d {dashboard.countdowns.lloyds.hours}h
                  </span>
                </div>
              </div>

              <div className={`p-3 rounded-lg border ${
                dashboard.countdowns.sec.days < 30 ? 'border-red-500/40 bg-red-500/5' : 'border-gray-800 bg-black/30'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase text-gray-500">SEC Filing</span>
                    <VerificationBadge status="official" size="xs" source="SEC" />
                  </div>
                  <span className={`text-lg font-bold ${dashboard.countdowns.sec.days < 30 ? 'text-red-400' : 'text-white'}`}>
                    {dashboard.countdowns.sec.days}d {dashboard.countdowns.sec.hours}h
                  </span>
                </div>
              </div>
            </div>

            {/* Active Alerts Count */}
            <div className="p-3 rounded-lg bg-black/30 border border-gray-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span className="text-[10px] uppercase text-gray-500">Active Alerts</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-xs font-bold">
                    {dashboard.alerts.filter(a => a.level === 'critical').length} Critical
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-xs font-bold">
                    {dashboard.alerts.filter(a => a.level === 'warning').length} Warning
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom: Data Sources Summary */}
        <div className="mt-6 pt-4 border-t border-gray-800/50">
          <div className="flex items-center justify-between text-[9px] text-gray-600">
            <div className="flex items-center gap-4">
              <span>Data Sources: COMEX, CME, SEC, OCC, Yahoo Finance, FRED</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Verified: Official exchange/regulatory data
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-orange-400" /> Rumored: Market speculation, requires confirmation
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
