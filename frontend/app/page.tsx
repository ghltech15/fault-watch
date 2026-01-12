'use client'

import { useQuery } from '@tanstack/react-query'
import { api, DashboardData, ContagionRiskData, CascadeData, OpportunitiesData } from '@/lib/api'
import { motion } from 'framer-motion'
import { AlertTriangle, TrendingDown, TrendingUp, Clock, Building2, Zap, BarChart3, Activity, Target, DollarSign, Layers, Gem } from 'lucide-react'

function formatNumber(num: number, decimals = 2): string {
  if (Math.abs(num) >= 1e9) return `$${(num / 1e9).toFixed(1)}B`
  if (Math.abs(num) >= 1e6) return `$${(num / 1e6).toFixed(1)}M`
  return `$${num.toFixed(decimals)}`
}

function formatCountdown(c: { days: number; hours: number; minutes: number }): string {
  return `${c.days}d ${c.hours}h ${c.minutes}m`
}

function CountdownTimer({ countdown, label }: { countdown: any; label: string }) {
  const isUrgent = countdown.days < 7
  const isCritical = countdown.days < 3

  return (
    <div className={`countdown ${isCritical ? 'text-danger' : isUrgent ? 'text-warning' : 'text-gray-400'}`}>
      <span className="text-xs uppercase tracking-wider opacity-60">{label}</span>
      <span className={`ml-2 font-bold ${isCritical ? 'animate-pulse' : ''}`}>
        {formatCountdown(countdown)}
      </span>
    </div>
  )
}

function RiskGauge({ value, label, color }: { value: number; label: string; color: string }) {
  const glowClass = value >= 7 ? 'glow-danger' : value >= 4 ? 'glow-warning' : 'glow-success'

  return (
    <motion.div
      className="text-center py-8"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-sm uppercase tracking-widest text-gray-500 mb-2">Systemic Risk Index</div>
      <div className={`text-8xl font-black ${glowClass}`} style={{ color }}>
        {value.toFixed(1)}
      </div>
      <div className={`badge mt-3`} style={{ backgroundColor: `${color}20`, color }}>
        {label}
      </div>
    </motion.div>
  )
}

function PriceCard({ prices }: { prices: Record<string, any> }) {
  const silver = prices.silver || { price: 0, change_pct: 0 }
  const gold = prices.gold || { price: 0, change_pct: 0 }
  const vix = prices.vix || { price: 0, change_pct: 0 }
  const ms = prices.morgan_stanley || { price: 0, change_pct: 0 }

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-success" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Live Prices</h3>
        <span className="w-2 h-2 rounded-full bg-success animate-pulse ml-auto" />
      </div>

      <div className="mb-4">
        <div className="text-xs text-gray-500 uppercase">Silver</div>
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold text-white">${silver.price.toFixed(2)}</span>
          <span className={`text-sm font-semibold ${silver.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
            {silver.change_pct >= 0 ? '+' : ''}{silver.change_pct.toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="text-xs text-gray-500">Gold</div>
          <div className="text-lg font-semibold">${gold.price.toFixed(0)}</div>
          <div className={`text-xs ${gold.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
            {gold.change_pct >= 0 ? '+' : ''}{gold.change_pct.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500">VIX</div>
          <div className="text-lg font-semibold">{vix.price.toFixed(1)}</div>
          <div className={`text-xs ${vix.change_pct <= 0 ? 'text-success' : 'text-danger'}`}>
            {vix.change_pct >= 0 ? '+' : ''}{vix.change_pct.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500">MS</div>
          <div className="text-lg font-semibold">${ms.price.toFixed(0)}</div>
          <div className={`text-xs ${ms.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
            {ms.change_pct >= 0 ? '+' : ''}{ms.change_pct.toFixed(1)}%
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function BankCard() {
  const { data: banks } = useQuery({ queryKey: ['banks'], queryFn: api.getBanks })

  const topBanks = banks?.filter(b => b.paper_loss && b.paper_loss > 0).slice(0, 3) || []

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Building2 className="w-5 h-5 text-danger" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Bank Exposure</h3>
      </div>

      <div className="space-y-3">
        {topBanks.map((bank) => {
          const lossRatio = bank.paper_loss! / bank.equity
          const isInsolvent = lossRatio > 1

          return (
            <div key={bank.ticker}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium">{bank.name}</span>
                <span className="text-sm text-danger font-semibold">
                  {formatNumber(bank.paper_loss!)}
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-danger rounded-full transition-all"
                  style={{ width: `${Math.min(lossRatio * 100, 100)}%` }}
                />
              </div>
              {isInsolvent && (
                <span className="badge badge-danger text-[10px] mt-1">INSOLVENT</span>
              )}
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

function DominoCard({ dominoes }: { dominoes: any[] }) {
  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-5 h-5 text-warning" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Domino Effect</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {dominoes.map((d, i) => (
          <div
            key={d.id}
            className="flex-1 min-w-[80px] p-2 rounded border text-center"
            style={{ borderColor: d.color, backgroundColor: `${d.color}10` }}
          >
            <div className="text-xs text-gray-400">{d.label}</div>
            <div className="text-sm font-bold" style={{ color: d.color }}>{d.status}</div>
            <div className="text-xs text-gray-500">{d.detail}</div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function AlertsCard({ alerts }: { alerts: any[] }) {
  const criticalCount = alerts.filter(a => a.level === 'critical').length

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-warning" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Alerts</h3>
        {criticalCount > 0 && (
          <span className="badge badge-danger ml-auto">{criticalCount}</span>
        )}
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-4 text-success">
            <span className="text-2xl">✓</span>
            <div className="text-sm mt-1">No active alerts</div>
          </div>
        ) : (
          alerts.slice(0, 5).map((alert, i) => (
            <div
              key={i}
              className={`p-2 rounded text-sm ${
                alert.level === 'critical' ? 'bg-danger/10 border-l-2 border-danger' :
                alert.level === 'warning' ? 'bg-warning/10 border-l-2 border-warning' :
                'bg-info/10 border-l-2 border-info'
              }`}
            >
              <div className="font-semibold">{alert.title}</div>
              <div className="text-xs text-gray-400">{alert.detail}</div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}

function ScenarioCard() {
  const { data: scenarios } = useQuery({ queryKey: ['scenarios'], queryFn: api.getScenarios })

  const scenario100 = scenarios?.silver_100

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-info" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Scenario: $100 Silver</h3>
      </div>

      {scenario100 && (
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-400">MS Loss</span>
            <span className="text-danger font-semibold">${scenario100.ms_loss.toFixed(0)}B</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Citi Loss</span>
            <span className="text-danger font-semibold">${scenario100.citi_loss.toFixed(0)}B</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">JPM Gain</span>
            <span className="text-success font-semibold">+${scenario100.jpm_gain.toFixed(0)}B</span>
          </div>
          <div className="border-t border-border pt-2 mt-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Fed Coverage</span>
              <span className="text-danger font-semibold">{scenario100.fed_coverage_pct.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

function CascadeCard() {
  const { data: cascade } = useQuery({ queryKey: ['cascade'], queryFn: api.getCascade, refetchInterval: 60000 })

  if (!cascade) return null

  const stageColors = ['#4ade80', '#84cc16', '#fbbf24', '#f97316', '#ef4444']
  const stageColor = stageColors[cascade.stage - 1] || '#4ade80'

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-5 h-5" style={{ color: stageColor }} />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Cascade Stage</h3>
      </div>

      <div className="text-center mb-4">
        <div className="text-6xl font-black" style={{ color: stageColor }}>
          {cascade.stage}
        </div>
        <div className="text-sm text-gray-400 mt-2">{cascade.description}</div>
      </div>

      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((s) => (
          <div
            key={s}
            className="flex-1 h-2 rounded"
            style={{
              backgroundColor: s <= cascade.stage ? stageColors[s - 1] : '#1f2937'
            }}
          />
        ))}
      </div>

      <div className="mt-3 text-xs text-gray-500 space-y-1">
        {Object.entries(cascade.stages).slice(0, 3).map(([num, desc]) => (
          <div key={num} className={parseInt(num) === cascade.stage ? 'text-white font-medium' : ''}>
            {num}. {desc.substring(0, 40)}...
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function ContagionCard() {
  const { data: contagion } = useQuery({ queryKey: ['contagion'], queryFn: api.getContagion, refetchInterval: 60000 })

  if (!contagion) return null

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5" style={{ color: contagion.contagion_color }} />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Contagion Risk</h3>
        <span
          className="badge ml-auto text-xs"
          style={{ backgroundColor: `${contagion.contagion_color}20`, color: contagion.contagion_color }}
        >
          {contagion.contagion_level.toUpperCase()}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-400">Score</span>
          <span className="font-bold" style={{ color: contagion.contagion_color }}>
            {contagion.contagion_score.toFixed(1)}/100
          </span>
        </div>
        <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{
              width: `${contagion.contagion_score}%`,
              backgroundColor: contagion.contagion_color
            }}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="text-xs text-gray-500">TED Spread</div>
          <div className="font-semibold">{contagion.credit_stress.ted_spread?.toFixed(2) || 'N/A'}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">HY Spread</div>
          <div className="font-semibold">{contagion.credit_stress.high_yield_spread?.toFixed(0) || 'N/A'}bp</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">CC Delinquency</div>
          <div className="font-semibold">{contagion.delinquencies.credit_card?.toFixed(1) || 'N/A'}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">COMEX Status</div>
          <div className={`font-semibold ${contagion.comex.status === 'elevated' || contagion.comex.status === 'critical' ? 'text-warning' : ''}`}>
            {contagion.comex.status.toUpperCase()}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function ComexCard() {
  const { data: contagion } = useQuery({ queryKey: ['contagion'], queryFn: api.getContagion, refetchInterval: 60000 })

  if (!contagion) return null

  const comex = contagion.comex
  const statusColors: Record<string, string> = {
    normal: '#4ade80',
    elevated: '#fbbf24',
    tight: '#f97316',
    critical: '#ef4444'
  }

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-warning" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">COMEX Silver</h3>
        <span
          className="badge ml-auto text-xs"
          style={{ backgroundColor: `${statusColors[comex.status]}20`, color: statusColors[comex.status] }}
        >
          {comex.status.toUpperCase()}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Registered (Deliverable)</span>
            <span className="font-semibold">{comex.registered_oz ? (comex.registered_oz / 1e6).toFixed(0) : 'N/A'}M oz</span>
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Open Interest</span>
            <span className="font-semibold">{comex.open_interest_oz ? (comex.open_interest_oz / 1e6).toFixed(0) : 'N/A'}M oz</span>
          </div>
        </div>
        <div className="border-t border-border pt-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Coverage Ratio</span>
            <span className={`font-bold ${(comex.coverage_ratio || 0) > 2 ? 'text-warning' : 'text-success'}`}>
              {comex.coverage_ratio?.toFixed(2) || 'N/A'}x
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {(comex.coverage_ratio || 0) > 3 ? 'CRITICAL: Paper claims exceed physical' :
             (comex.coverage_ratio || 0) > 2 ? 'ELEVATED: Watch for delivery squeeze' :
             'Normal levels'}
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Days of Supply</span>
            <span className="font-semibold">{comex.days_of_supply?.toFixed(0) || 'N/A'} days</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function OpportunitiesCard() {
  const { data: opportunities } = useQuery({ queryKey: ['opportunities'], queryFn: api.getOpportunities, refetchInterval: 300000 })

  if (!opportunities) return null

  const riskColors: Record<string, string> = {
    low: '#4ade80',
    medium: '#fbbf24',
    high: '#f97316',
    very_high: '#ef4444'
  }

  return (
    <motion.div
      className="card cursor-pointer lg:col-span-2"
      whileHover={{ scale: 1.01 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.9 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-success" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Investment Opportunities</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <div className="text-xs text-gray-500 uppercase mb-2">Under $100</div>
          <div className="space-y-2">
            {opportunities.under_100.slice(0, 3).map((play) => (
              <div key={play.ticker} className="p-2 rounded bg-gray-800/50">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white">{play.ticker}</span>
                  <span className="text-success">${play.price?.toFixed(2)}</span>
                </div>
                <div className="text-xs text-gray-400">{play.name}</div>
                <div className="text-xs mt-1" style={{ color: riskColors[play.risk] }}>
                  {play.thesis}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 uppercase mb-2">Under $500</div>
          <div className="space-y-2">
            {opportunities.under_500.slice(0, 3).map((play) => (
              <div key={play.ticker} className="p-2 rounded bg-gray-800/50">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white">{play.ticker}</span>
                  <span className="text-success">${play.price?.toFixed(2)}</span>
                </div>
                <div className="text-xs text-gray-400">{play.name}</div>
                <div className="text-xs mt-1" style={{ color: riskColors[play.risk] }}>
                  {play.thesis}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 uppercase mb-2">Leveraged ETFs</div>
          <div className="space-y-2">
            {opportunities.leveraged.length > 0 ? opportunities.leveraged.slice(0, 3).map((play) => (
              <div key={play.ticker} className="p-2 rounded bg-gray-800/50">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white">{play.ticker}</span>
                  <span className="text-success">${play.price?.toFixed(2)}</span>
                </div>
                <div className="text-xs text-gray-400">{play.name}</div>
                <div className="text-xs mt-1" style={{ color: riskColors[play.risk] }}>
                  {play.thesis}
                </div>
              </div>
            )) : (
              <div className="text-xs text-gray-500 p-2">Loading...</div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-3 text-[10px] text-gray-600 text-center">
        {opportunities.disclaimer}
      </div>
    </motion.div>
  )
}

function MinersCard() {
  const { data: miners } = useQuery({ queryKey: ['miners'], queryFn: api.getMiners, refetchInterval: 60000 })

  if (!miners) return null

  const leverageColors: Record<string, string> = {
    medium: '#84cc16',
    high: '#f97316',
    very_high: '#ef4444'
  }

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Gem className="w-5 h-5 text-gray-400" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Junior Silver Miners</h3>
      </div>

      <div className="space-y-2">
        {miners.slice(0, 5).map((miner) => (
          <div key={miner.ticker} className="flex items-center justify-between py-1 border-b border-gray-800 last:border-0">
            <div>
              <span className="font-bold text-white">{miner.ticker}</span>
              <span className="text-xs text-gray-500 ml-2">{miner.name}</span>
            </div>
            <div className="text-right">
              <div className="font-semibold">${miner.price?.toFixed(2) || 'N/A'}</div>
              <div className="text-xs" style={{ color: leverageColors[miner.leverage_level] }}>
                {miner.potential_multiple}
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function SectorsCard() {
  const { data: contagion } = useQuery({ queryKey: ['contagion'], queryFn: api.getContagion, refetchInterval: 60000 })

  if (!contagion) return null

  const riskColors: Record<string, string> = {
    low: '#4ade80',
    medium: '#fbbf24',
    high: '#f97316',
    critical: '#ef4444'
  }

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.1 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <TrendingDown className="w-5 h-5 text-danger" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Sector Contagion</h3>
      </div>

      <div className="space-y-2 max-h-60 overflow-y-auto">
        {contagion.sectors.slice(0, 6).map((sector) => (
          <div key={sector.id} className="p-2 rounded bg-gray-800/50">
            <div className="flex justify-between items-center mb-1">
              <span className="font-medium text-white text-sm">{sector.name}</span>
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{ backgroundColor: `${riskColors[sector.risk_level]}20`, color: riskColors[sector.risk_level] }}
              >
                {sector.risk_level.toUpperCase()}
              </span>
            </div>
            {sector.etf && (
              <div className="text-xs text-gray-400">
                ETF: {sector.etf} {sector.current_price ? `$${sector.current_price.toFixed(2)}` : ''}
                {sector.change_pct !== null && (
                  <span className={sector.change_pct >= 0 ? 'text-success' : 'text-danger'}>
                    {' '}({sector.change_pct >= 0 ? '+' : ''}{sector.change_pct.toFixed(1)}%)
                  </span>
                )}
              </div>
            )}
            <div className="text-xs text-gray-500 mt-1">{sector.why_collapse}</div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
    refetchInterval: 60000,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-danger border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <div className="text-gray-400">Loading dashboard...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center text-danger">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <div>Failed to load dashboard</div>
          <div className="text-sm text-gray-400 mt-2">Check API connection</div>
        </div>
      </div>
    )
  }

  const dashboard = data as DashboardData

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <h1 className="text-xl font-black text-white">fault.watch</h1>

          <div className="flex items-center gap-6">
            <CountdownTimer countdown={dashboard.countdowns.lloyds} label="Lloyd's" />
            <CountdownTimer countdown={dashboard.countdowns.sec} label="SEC" />
            <div className="text-xs text-gray-500">
              Updated {new Date(dashboard.last_updated).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      {/* Alert Banner */}
      {dashboard.alerts.some(a => a.level === 'critical') && (
        <div className="bg-danger/90 text-white py-2 px-4 text-center animate-pulse">
          <span className="font-bold mr-2">[BREAKING]</span>
          {dashboard.alerts.find(a => a.level === 'critical')?.title}
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Hero */}
        <RiskGauge
          value={dashboard.risk_index}
          label={dashboard.risk_label}
          color={dashboard.risk_color}
        />

        {/* Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
          <PriceCard prices={dashboard.prices} />
          <CascadeCard />
          <ContagionCard />
          <BankCard />
          <DominoCard dominoes={dashboard.dominoes} />
          <ComexCard />
          <AlertsCard alerts={dashboard.alerts} />
          <ScenarioCard />
          <SectorsCard />
          <MinersCard />
          <OpportunitiesCard />
        </div>
      </main>
    </div>
  )
}
