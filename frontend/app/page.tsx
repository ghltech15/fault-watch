'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, DashboardData, ContagionRiskData, CascadeData, OpportunitiesData } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, TrendingDown, TrendingUp, Clock, Building2, Zap, BarChart3, Activity, Target, DollarSign, Layers, Gem, X, ChevronRight } from 'lucide-react'

type CardType = 'prices' | 'cascade' | 'contagion' | 'banks' | 'dominoes' | 'comex' | 'alerts' | 'scenarios' | 'sectors' | 'miners' | 'opportunities' | null

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

// Modal Component
function Modal({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
        <motion.div
          className="relative bg-card border border-border rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
        >
          <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">{title}</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="p-6">
            {children}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Detailed Views for each card type
function PricesDetailView({ prices }: { prices: Record<string, any> }) {
  const allPrices = [
    { key: 'silver', label: 'Silver (SLV)', data: prices.silver },
    { key: 'gold', label: 'Gold (GLD)', data: prices.gold },
    { key: 'vix', label: 'VIX (Fear Index)', data: prices.vix },
    { key: 'morgan_stanley', label: 'Morgan Stanley', data: prices.morgan_stanley },
    { key: 'citigroup', label: 'Citigroup', data: prices.citigroup },
    { key: 'jpmorgan', label: 'JPMorgan Chase', data: prices.jpmorgan },
  ]

  return (
    <div className="space-y-6">
      <p className="text-gray-400">Real-time price tracking for key assets in the silver squeeze thesis.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {allPrices.map(({ key, label, data }) => data && (
          <div key={key} className="p-4 bg-gray-800/50 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">{label}</div>
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-bold">${data.price?.toFixed(2)}</span>
              <span className={`text-lg font-semibold ${data.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                {data.change_pct >= 0 ? '+' : ''}{data.change_pct?.toFixed(2)}%
              </span>
            </div>
            {data.week_change !== undefined && (
              <div className="text-sm text-gray-500 mt-1">
                Weekly: <span className={data.week_change >= 0 ? 'text-success' : 'text-danger'}>
                  {data.week_change >= 0 ? '+' : ''}{data.week_change?.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="border-t border-border pt-4">
        <h4 className="font-semibold mb-2">Why These Prices Matter</h4>
        <ul className="text-sm text-gray-400 space-y-2">
          <li><ChevronRight className="w-4 h-4 inline text-warning" /> <strong>Silver:</strong> Main catalyst - rising prices pressure bank short positions</li>
          <li><ChevronRight className="w-4 h-4 inline text-warning" /> <strong>Gold:</strong> Safe haven indicator - rises during financial stress</li>
          <li><ChevronRight className="w-4 h-4 inline text-warning" /> <strong>VIX:</strong> Fear gauge - spikes signal market panic</li>
          <li><ChevronRight className="w-4 h-4 inline text-warning" /> <strong>Bank Stocks:</strong> Direct exposure - falling prices indicate trouble</li>
        </ul>
      </div>
    </div>
  )
}

function CascadeDetailView() {
  const { data: cascade } = useQuery({ queryKey: ['cascade'], queryFn: api.getCascade })

  if (!cascade) return <div className="text-gray-400">Loading...</div>

  const stageDetails = [
    { stage: 1, name: 'Stable', desc: 'Markets functioning normally. Silver shorts manageable. No stress signals.', color: '#4ade80' },
    { stage: 2, name: 'Elevated', desc: 'Credit spreads widening. Silver delivery pressure building. Early stress indicators.', color: '#84cc16' },
    { stage: 3, name: 'Stressed', desc: 'Bank losses materializing. COMEX inventory declining. Credit markets tightening.', color: '#fbbf24' },
    { stage: 4, name: 'Critical', desc: 'Bank insolvency imminent. Margin calls cascading. Flight to safety accelerating.', color: '#f97316' },
    { stage: 5, name: 'Systemic', desc: 'Multiple bank failures. Credit frozen. Fed emergency intervention likely.', color: '#ef4444' },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center py-6">
        <div className="text-7xl font-black" style={{ color: stageDetails[cascade.stage - 1].color }}>
          Stage {cascade.stage}
        </div>
        <div className="text-xl text-gray-400 mt-2">{stageDetails[cascade.stage - 1].name}</div>
      </div>

      <div className="flex gap-2 mb-6">
        {stageDetails.map((s) => (
          <div
            key={s.stage}
            className={`flex-1 h-3 rounded transition-all ${cascade.stage >= s.stage ? '' : 'opacity-30'}`}
            style={{ backgroundColor: s.color }}
          />
        ))}
      </div>

      <div className="space-y-3">
        {stageDetails.map((s) => (
          <div
            key={s.stage}
            className={`p-4 rounded-lg border-l-4 ${cascade.stage === s.stage ? 'bg-gray-800' : 'bg-gray-900/50'}`}
            style={{ borderColor: s.color }}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold" style={{ color: s.color }}>{s.stage}</span>
              <div>
                <div className="font-semibold text-white">{s.name}</div>
                <div className="text-sm text-gray-400">{s.desc}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ContagionDetailView() {
  const { data: contagion } = useQuery({ queryKey: ['contagion'], queryFn: api.getContagion })

  if (!contagion) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <div className="text-center py-4">
        <div className="text-6xl font-black" style={{ color: contagion.contagion_color }}>
          {contagion.contagion_score.toFixed(0)}
        </div>
        <div className="text-gray-400 mt-1">Contagion Score (0-100)</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-warning" /> Credit Stress
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">TED Spread</span>
              <span>{contagion.credit_stress.ted_spread?.toFixed(3) || 'N/A'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Credit Spread</span>
              <span>{contagion.credit_stress.credit_spread?.toFixed(2) || 'N/A'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">High Yield Spread</span>
              <span>{contagion.credit_stress.high_yield_spread?.toFixed(0) || 'N/A'} bp</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">SOFR Rate</span>
              <span>{contagion.credit_stress.sofr_rate?.toFixed(2) || 'N/A'}%</span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-success" /> Liquidity
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Reverse Repo</span>
              <span>${(contagion.liquidity.reverse_repo || 0) / 1e9}B</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Bank Deposits</span>
              <span>${((contagion.liquidity.bank_deposits || 0) / 1e12).toFixed(1)}T</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Deposit Change</span>
              <span className={contagion.liquidity.deposit_change_pct && contagion.liquidity.deposit_change_pct < 0 ? 'text-danger' : ''}>
                {contagion.liquidity.deposit_change_pct?.toFixed(2) || 'N/A'}%
              </span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-danger" /> Delinquencies
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Credit Card</span>
              <span className={contagion.delinquencies.credit_card && contagion.delinquencies.credit_card > 3 ? 'text-danger' : ''}>
                {contagion.delinquencies.credit_card?.toFixed(2) || 'N/A'}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Auto Loan</span>
              <span>{contagion.delinquencies.auto_loan?.toFixed(2) || 'N/A'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Mortgage</span>
              <span>{contagion.delinquencies.mortgage?.toFixed(2) || 'N/A'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Trend</span>
              <span className={contagion.delinquencies.trend === 'rising' ? 'text-danger' : 'text-success'}>
                {contagion.delinquencies.trend?.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-warning" /> COMEX Inventory
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Registered</span>
              <span>{contagion.comex.registered_oz ? (contagion.comex.registered_oz / 1e6).toFixed(1) : 'N/A'}M oz</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Open Interest</span>
              <span>{contagion.comex.open_interest_oz ? (contagion.comex.open_interest_oz / 1e6).toFixed(1) : 'N/A'}M oz</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Coverage Ratio</span>
              <span className={contagion.comex.coverage_ratio && contagion.comex.coverage_ratio > 2 ? 'text-warning' : ''}>
                {contagion.comex.coverage_ratio?.toFixed(2) || 'N/A'}x
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function BanksDetailView() {
  const { data: banks } = useQuery({ queryKey: ['banks'], queryFn: api.getBanks })

  if (!banks) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <p className="text-gray-400">Bank exposure to silver short positions and potential losses at current prices.</p>

      <div className="space-y-4">
        {banks.map((bank) => {
          const lossRatio = bank.paper_loss ? bank.paper_loss / bank.equity : 0
          const isInsolvent = lossRatio > 1

          return (
            <div key={bank.ticker} className="p-4 bg-gray-800/50 rounded-lg">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="font-bold text-lg text-white">{bank.name}</div>
                  <div className="text-sm text-gray-400">{bank.ticker}</div>
                </div>
                {isInsolvent && <span className="badge badge-danger">INSOLVENT</span>}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-500">Position</div>
                  <div className="font-semibold">{bank.position || 'Unknown'}</div>
                </div>
                <div>
                  <div className="text-gray-500">Ounces</div>
                  <div className="font-semibold">{bank.ounces ? `${(bank.ounces / 1e9).toFixed(2)}B` : 'N/A'}</div>
                </div>
                <div>
                  <div className="text-gray-500">Equity</div>
                  <div className="font-semibold">{formatNumber(bank.equity)}</div>
                </div>
                <div>
                  <div className="text-gray-500">Paper Loss</div>
                  <div className="font-semibold text-danger">{bank.paper_loss ? formatNumber(bank.paper_loss) : 'N/A'}</div>
                </div>
              </div>

              {bank.paper_loss && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Loss vs Equity</span>
                    <span>{(lossRatio * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-danger rounded-full"
                      style={{ width: `${Math.min(lossRatio * 100, 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function AlertsDetailView({ alerts }: { alerts: any[] }) {
  return (
    <div className="space-y-4">
      <p className="text-gray-400">All active alerts and notifications from the system.</p>

      {alerts.length === 0 ? (
        <div className="text-center py-12 text-success">
          <span className="text-6xl">✓</span>
          <div className="text-xl mt-4">No Active Alerts</div>
          <div className="text-gray-400 mt-2">System is operating normally</div>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert, i) => (
            <div
              key={i}
              className={`p-4 rounded-lg border-l-4 ${
                alert.level === 'critical' ? 'bg-danger/10 border-danger' :
                alert.level === 'warning' ? 'bg-warning/10 border-warning' :
                'bg-info/10 border-info'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className={`badge text-xs ${
                  alert.level === 'critical' ? 'badge-danger' :
                  alert.level === 'warning' ? 'badge-warning' :
                  'badge-info'
                }`}>
                  {alert.level.toUpperCase()}
                </span>
                <span className="font-bold text-white">{alert.title}</span>
              </div>
              <div className="text-gray-400">{alert.detail}</div>
              {alert.action && (
                <div className="mt-2 text-sm text-info">Action: {alert.action}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ScenariosDetailView() {
  const { data: scenarios } = useQuery({ queryKey: ['scenarios'], queryFn: api.getScenarios })

  if (!scenarios) return <div className="text-gray-400">Loading...</div>

  const scenarioList = [
    { price: 50, data: scenarios.silver_50 },
    { price: 75, data: scenarios.silver_75 },
    { price: 100, data: scenarios.silver_100 },
    { price: 150, data: scenarios.silver_150 },
    { price: 200, data: scenarios.silver_200 },
  ].filter(s => s.data)

  return (
    <div className="space-y-6">
      <p className="text-gray-400">Projected bank losses at various silver price levels.</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-2 text-gray-400">Silver Price</th>
              <th className="text-right py-3 px-2 text-gray-400">MS Loss</th>
              <th className="text-right py-3 px-2 text-gray-400">Citi Loss</th>
              <th className="text-right py-3 px-2 text-gray-400">JPM Gain</th>
              <th className="text-right py-3 px-2 text-gray-400">Fed Coverage</th>
              <th className="text-center py-3 px-2 text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {scenarioList.map(({ price, data }) => (
              <tr key={price} className="border-b border-gray-800">
                <td className="py-3 px-2 font-bold text-white">${price}</td>
                <td className="py-3 px-2 text-right text-danger">${data.ms_loss.toFixed(0)}B</td>
                <td className="py-3 px-2 text-right text-danger">${data.citi_loss.toFixed(0)}B</td>
                <td className="py-3 px-2 text-right text-success">+${data.jpm_gain.toFixed(0)}B</td>
                <td className="py-3 px-2 text-right text-danger">{data.fed_coverage_pct.toFixed(0)}%</td>
                <td className="py-3 px-2 text-center">
                  {data.ms_insolvent || data.citi_insolvent ? (
                    <span className="badge badge-danger text-xs">INSOLVENT</span>
                  ) : (
                    <span className="badge text-xs bg-gray-700">Solvent</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-border pt-4">
        <h4 className="font-semibold mb-2">Key Insights</h4>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• Morgan Stanley becomes insolvent around $75 silver</li>
          <li>• Citigroup follows at approximately $100 silver</li>
          <li>• JPMorgan profits from long position</li>
          <li>• Fed coverage indicates % of losses Fed must backstop</li>
        </ul>
      </div>
    </div>
  )
}

function SectorsDetailView() {
  const { data: contagion } = useQuery({ queryKey: ['contagion'], queryFn: api.getContagion })

  if (!contagion) return <div className="text-gray-400">Loading...</div>

  const riskColors: Record<string, string> = {
    low: '#4ade80',
    medium: '#fbbf24',
    high: '#f97316',
    critical: '#ef4444'
  }

  return (
    <div className="space-y-6">
      <p className="text-gray-400">Sectors vulnerable to contagion from a banking crisis, with ETF plays for each.</p>

      <div className="space-y-4">
        {contagion.sectors.map((sector) => (
          <div key={sector.id} className="p-4 bg-gray-800/50 rounded-lg">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-bold text-lg text-white">{sector.name}</div>
                <div className="text-sm text-gray-400">{sector.why_collapse}</div>
              </div>
              <span
                className="badge text-xs"
                style={{ backgroundColor: `${riskColors[sector.risk_level]}20`, color: riskColors[sector.risk_level] }}
              >
                {sector.risk_level.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
              {sector.etf && (
                <div>
                  <div className="text-gray-500">Long ETF</div>
                  <div className="font-semibold">{sector.etf}</div>
                  {sector.current_price && (
                    <div className="text-xs text-gray-400">${sector.current_price.toFixed(2)}</div>
                  )}
                </div>
              )}
              {sector.inverse_etf && (
                <div>
                  <div className="text-gray-500">Inverse ETF</div>
                  <div className="font-semibold text-success">{sector.inverse_etf}</div>
                </div>
              )}
              <div>
                <div className="text-gray-500">Daily Change</div>
                <div className={`font-semibold ${sector.change_pct && sector.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                  {sector.change_pct !== null ? `${sector.change_pct >= 0 ? '+' : ''}${sector.change_pct.toFixed(2)}%` : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-gray-500">Contagion Score</div>
                <div className="font-semibold">{sector.contagion_score}/100</div>
              </div>
            </div>

            {sector.investment_plays.length > 0 && (
              <div className="border-t border-gray-700 pt-3">
                <div className="text-xs text-gray-500 mb-2">Investment Plays</div>
                <div className="flex flex-wrap gap-2">
                  {sector.investment_plays.map((play, i) => (
                    <span key={i} className="text-xs bg-gray-700 px-2 py-1 rounded">{play}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function MinersDetailView() {
  const { data: miners } = useQuery({ queryKey: ['miners'], queryFn: api.getMiners })

  if (!miners) return <div className="text-gray-400">Loading...</div>

  const leverageColors: Record<string, string> = {
    medium: '#84cc16',
    high: '#f97316',
    very_high: '#ef4444'
  }

  return (
    <div className="space-y-6">
      <p className="text-gray-400">Junior silver miners offer leveraged exposure to silver price moves. Higher leverage = higher risk/reward.</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-2 text-gray-400">Ticker</th>
              <th className="text-left py-3 px-2 text-gray-400">Company</th>
              <th className="text-right py-3 px-2 text-gray-400">Price</th>
              <th className="text-right py-3 px-2 text-gray-400">Change</th>
              <th className="text-center py-3 px-2 text-gray-400">Leverage</th>
              <th className="text-right py-3 px-2 text-gray-400">Potential</th>
            </tr>
          </thead>
          <tbody>
            {miners.map((miner) => (
              <tr key={miner.ticker} className="border-b border-gray-800">
                <td className="py-3 px-2 font-bold text-white">{miner.ticker}</td>
                <td className="py-3 px-2">{miner.name}</td>
                <td className="py-3 px-2 text-right">${miner.price?.toFixed(2) || 'N/A'}</td>
                <td className={`py-3 px-2 text-right ${miner.change_pct && miner.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                  {miner.change_pct !== null ? `${miner.change_pct >= 0 ? '+' : ''}${miner.change_pct.toFixed(2)}%` : 'N/A'}
                </td>
                <td className="py-3 px-2 text-center">
                  <span
                    className="badge text-xs"
                    style={{ backgroundColor: `${leverageColors[miner.leverage_level]}20`, color: leverageColors[miner.leverage_level] }}
                  >
                    {miner.leverage_level.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td className="py-3 px-2 text-right text-success">{miner.potential_multiple || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-border pt-4">
        <h4 className="font-semibold mb-2">Risk Warning</h4>
        <p className="text-sm text-gray-400">
          Junior miners are highly speculative. Many fail. Leverage works both ways -
          a 3x miner can lose 30% when silver drops 10%. Only invest what you can afford to lose.
        </p>
      </div>
    </div>
  )
}

function OpportunitiesDetailView() {
  const { data: opportunities } = useQuery({ queryKey: ['opportunities'], queryFn: api.getOpportunities })

  if (!opportunities) return <div className="text-gray-400">Loading...</div>

  const riskColors: Record<string, string> = {
    low: '#4ade80',
    medium: '#fbbf24',
    high: '#f97316',
    very_high: '#ef4444'
  }

  const renderPlays = (plays: any[], title: string) => (
    <div>
      <h4 className="font-semibold text-lg mb-3">{title}</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {plays.map((play) => (
          <div key={play.ticker} className="p-3 bg-gray-800/50 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <div>
                <span className="font-bold text-white">{play.ticker}</span>
                <span className="text-xs text-gray-400 ml-2">{play.type}</span>
              </div>
              <span className="text-success font-semibold">${play.price?.toFixed(2)}</span>
            </div>
            <div className="text-sm text-gray-400 mb-2">{play.name}</div>
            <div className="text-sm">{play.thesis}</div>
            <div className="mt-2">
              <span
                className="badge text-xs"
                style={{ backgroundColor: `${riskColors[play.risk]}20`, color: riskColors[play.risk] }}
              >
                {play.risk.replace('_', ' ').toUpperCase()} RISK
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="space-y-8">
      <p className="text-gray-400">Investment opportunities categorized by budget. Higher risk plays offer more upside but can lose everything.</p>

      {opportunities.under_100.length > 0 && renderPlays(opportunities.under_100, 'Under $100')}
      {opportunities.under_500.length > 0 && renderPlays(opportunities.under_500, 'Under $500')}
      {opportunities.leveraged.length > 0 && renderPlays(opportunities.leveraged, 'Leveraged ETFs')}

      <div className="border-t border-border pt-4">
        <div className="text-xs text-gray-500 text-center">{opportunities.disclaimer}</div>
      </div>
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
      className="card cursor-pointer"
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
  const [expandedCard, setExpandedCard] = useState<CardType>(null)

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
          <div onClick={() => setExpandedCard('prices')}><PriceCard prices={dashboard.prices} /></div>
          <div onClick={() => setExpandedCard('cascade')}><CascadeCard /></div>
          <div onClick={() => setExpandedCard('contagion')}><ContagionCard /></div>
          <div onClick={() => setExpandedCard('banks')}><BankCard /></div>
          <div onClick={() => setExpandedCard('dominoes')}><DominoCard dominoes={dashboard.dominoes} /></div>
          <div onClick={() => setExpandedCard('comex')}><ContagionCard /></div>
          <div onClick={() => setExpandedCard('alerts')}><AlertsCard alerts={dashboard.alerts} /></div>
          <div onClick={() => setExpandedCard('scenarios')}><ScenarioCard /></div>
          <div onClick={() => setExpandedCard('sectors')}><SectorsCard /></div>
          <div onClick={() => setExpandedCard('miners')}><MinersCard /></div>
          <div onClick={() => setExpandedCard('opportunities')} className="lg:col-span-2"><OpportunitiesCard /></div>
        </div>
      </main>

      {/* Detail Modals */}
      <Modal isOpen={expandedCard === 'prices'} onClose={() => setExpandedCard(null)} title="Live Prices">
        <PricesDetailView prices={dashboard.prices} />
      </Modal>

      <Modal isOpen={expandedCard === 'cascade'} onClose={() => setExpandedCard(null)} title="Cascade Stage">
        <CascadeDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'contagion'} onClose={() => setExpandedCard(null)} title="Contagion Risk Analysis">
        <ContagionDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'banks'} onClose={() => setExpandedCard(null)} title="Bank Exposure">
        <BanksDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'dominoes'} onClose={() => setExpandedCard(null)} title="Domino Effect">
        <AlertsDetailView alerts={dashboard.alerts} />
      </Modal>

      <Modal isOpen={expandedCard === 'comex'} onClose={() => setExpandedCard(null)} title="COMEX Silver Inventory">
        <ContagionDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'alerts'} onClose={() => setExpandedCard(null)} title="System Alerts">
        <AlertsDetailView alerts={dashboard.alerts} />
      </Modal>

      <Modal isOpen={expandedCard === 'scenarios'} onClose={() => setExpandedCard(null)} title="Silver Price Scenarios">
        <ScenariosDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'sectors'} onClose={() => setExpandedCard(null)} title="Sector Contagion">
        <SectorsDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'miners'} onClose={() => setExpandedCard(null)} title="Junior Silver Miners">
        <MinersDetailView />
      </Modal>

      <Modal isOpen={expandedCard === 'opportunities'} onClose={() => setExpandedCard(null)} title="Investment Opportunities">
        <OpportunitiesDetailView />
      </Modal>
    </div>
  )
}
