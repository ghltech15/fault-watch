'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, DashboardData, ContagionRiskData, CascadeData, OpportunitiesData, NakedShortAnalysis, AlertData, TheoryData, CrisisGaugeData, CrisisScannerData } from '@/lib/api'
import { VerificationBadge, VerificationDot, CardHeader, VerificationLegend } from '@/components/VerificationBadge'
import { CrisisGaugeCard, CrisisGaugeDetailView } from '@/components/CrisisGauge'
import { GovernmentInterventionCard, GovernmentInterventionDetailView } from '@/components/GovernmentIntervention'
import { FaultWatchAlertsCard, FaultWatchAlertsDetailView } from '@/components/FaultWatchAlerts'
import { CrisisSearchPadCard, CrisisSearchPadDetailView } from '@/components/CrisisSearchPad'
import { RiskMatrixCard, RiskMatrixDetailView } from '@/components/RiskMatrix'
import { PossibleOutlookCard, PossibleOutlookDetailView } from '@/components/PossibleOutlook'
import { ExecutiveSummary } from '@/components/ExecutiveSummary'
import { CrisisScanner } from '@/components/CrisisScanner'
import { UserRegistrationCard, AccessGate, useUserAccess, FeedbackCard, CommunityStatsCard } from '@/components/UserRegistration'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, TrendingDown, TrendingUp, Clock, Building2, Zap, BarChart3, Activity, Target, DollarSign, Layers, Gem, X, ChevronRight, Skull, Scale, Radio, ChevronDown, ChevronUp, Shield } from 'lucide-react'

type CardType = 'prices' | 'contagion' | 'banks' | 'comex' | 'alerts' | 'theories' | 'scenarios' | 'sectors' | 'miners' | 'opportunities' | 'naked-shorts' | 'crisis-gauge' | 'government' | 'fault-watch-alerts' | 'crisis-search-pad' | 'risk-matrix' | 'possible-outlook' | null

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

function AlertsDetailView({ alerts }: { alerts: AlertData[] }) {
  // Filter to verified alerts only
  const verifiedAlerts = alerts.filter(a =>
    a.verification_status === 'verified' && !a.is_hypothetical
  )

  return (
    <div className="space-y-4">
      <p className="text-gray-400">
        Verified alerts based on real-time market data. Only alerts backed by official sources are shown here.
      </p>

      {verifiedAlerts.length === 0 ? (
        <div className="text-center py-12 text-success">
          <span className="text-6xl">✓</span>
          <div className="text-xl mt-4">No Verified Alerts</div>
          <div className="text-gray-400 mt-2">All monitored systems are operating normally</div>
        </div>
      ) : (
        <div className="space-y-3">
          {verifiedAlerts.map((alert, i) => (
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
                <VerificationBadge
                  status={alert.verification_status}
                  sourceCount={alert.source_count}
                  size="sm"
                />
              </div>
              <div className="text-gray-400">{alert.detail}</div>
              {alert.action && (
                <div className="mt-2 text-sm text-info">Source: {alert.action}</div>
              )}
              {alert.sources && alert.sources.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Sources: {alert.sources.map(s => s.name).join(', ')}
                </div>
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

function NakedShortsDetailView() {
  const { data: nakedShorts } = useQuery({ queryKey: ['naked-shorts'], queryFn: api.getNakedShorts })

  if (!nakedShorts) return <div className="text-gray-400">Loading...</div>

  const positionColors: Record<string, string> = {
    SHORT: '#ef4444',
    LONG: '#4ade80'
  }

  return (
    <div className="space-y-6">
      <div className="p-4 bg-danger/10 border border-danger/30 rounded-lg text-center">
        <div className="text-2xl font-bold text-danger mb-2">{nakedShorts.verdict}</div>
        <p className="text-gray-400">Banks have sold 30x more silver than physically exists. When delivery is demanded, there is no silver to deliver.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-gray-800/50 rounded-lg text-center">
          <div className="text-xs text-gray-500 mb-1">Total Short Position</div>
          <div className="text-3xl font-bold text-danger">{(nakedShorts.total_short_oz / 1e9).toFixed(2)}B oz</div>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg text-center">
          <div className="text-xs text-gray-500 mb-1">Physical Available</div>
          <div className="text-3xl font-bold text-warning">{(nakedShorts.available_physical_oz / 1e9).toFixed(0)}B oz</div>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg text-center">
          <div className="text-xs text-gray-500 mb-1">Paper to Physical</div>
          <div className="text-3xl font-bold text-danger">{nakedShorts.paper_to_physical_ratio}:1</div>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg text-center">
          <div className="text-xs text-gray-500 mb-1">Years of Production</div>
          <div className="text-3xl font-bold text-warning">{nakedShorts.years_of_production} years</div>
        </div>
      </div>

      <div>
        <h4 className="font-semibold text-lg mb-3">Bank Short Positions</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 text-gray-400">Bank</th>
                <th className="text-center py-3 px-2 text-gray-400">Position</th>
                <th className="text-right py-3 px-2 text-gray-400">Ounces</th>
                <th className="text-right py-3 px-2 text-gray-400">Equity</th>
                <th className="text-center py-3 px-2 text-gray-400">Deadline</th>
                <th className="text-center py-3 px-2 text-gray-400">Regulator</th>
                <th className="text-right py-3 px-2 text-gray-400">@$80 Risk</th>
              </tr>
            </thead>
            <tbody>
              {nakedShorts.bank_positions.map((bank) => (
                <tr key={bank.ticker} className="border-b border-gray-800">
                  <td className="py-3 px-2">
                    <div className="font-bold text-white">{bank.name}</div>
                    <div className="text-xs text-gray-500">{bank.ticker}</div>
                  </td>
                  <td className="py-3 px-2 text-center">
                    <span
                      className="badge text-xs"
                      style={{ backgroundColor: `${positionColors[bank.position]}20`, color: positionColors[bank.position] }}
                    >
                      {bank.position}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right font-semibold">{(bank.ounces / 1e9).toFixed(2)}B</td>
                  <td className="py-3 px-2 text-right">${(bank.equity / 1e9).toFixed(0)}B</td>
                  <td className="py-3 px-2 text-center text-gray-400">{bank.deadline || '-'}</td>
                  <td className="py-3 px-2 text-center text-gray-400">{bank.regulator || '-'}</td>
                  <td className="py-3 px-2 text-right">
                    {bank.position === 'LONG' ? (
                      <span className="text-success font-bold">PROFIT</span>
                    ) : bank.loss_ratio_at_80 ? (
                      <span className={bank.loss_ratio_at_80 > 1 ? 'text-danger font-bold' : 'text-warning'}>
                        {bank.loss_ratio_at_80.toFixed(1)}x equity
                      </span>
                    ) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-danger/10 rounded-lg">
          <h5 className="font-semibold text-danger mb-2">Banks Insolvent at $80 Silver</h5>
          <ul className="text-sm space-y-1">
            {nakedShorts.banks_insolvent_at_80.map((bank) => (
              <li key={bank}>• {bank}</li>
            ))}
          </ul>
        </div>
        <div className="p-4 bg-warning/10 rounded-lg">
          <h5 className="font-semibold text-warning mb-2">Banks Insolvent at $100 Silver</h5>
          <ul className="text-sm space-y-1">
            {nakedShorts.banks_insolvent_at_100.map((bank) => (
              <li key={bank}>• {bank}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-border pt-4">
        <h5 className="font-semibold mb-2">Key Deadlines</h5>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Lloyd&apos;s/HSBC:</span>
            <span className="ml-2 font-semibold">{nakedShorts.lloyds_deadline}</span>
          </div>
          <div>
            <span className="text-gray-400">SEC/MS:</span>
            <span className="ml-2 font-semibold">{nakedShorts.sec_deadline}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Crisis Command Center Hero
function CrisisCommandCenter({ dashboard }: { dashboard: DashboardData }) {
  const { data: crisisData } = useQuery({ queryKey: ['crisis-gauge'], queryFn: api.getCrisisGauge, refetchInterval: 30000 })
  const { data: nakedShorts } = useQuery({ queryKey: ['naked-shorts'], queryFn: api.getNakedShorts, refetchInterval: 60000 })

  const silver = dashboard.prices.silver || { price: 0, change_pct: 0 }
  const silverMove = crisisData ? crisisData.silver_move : silver.price - 30
  const totalLoss = crisisData ? crisisData.losses.reduce((sum, l) => sum + l.total_loss, 0) : 0
  const cracksShowing = crisisData ? crisisData.cracks_showing_count : 0
  const totalCracks = crisisData ? crisisData.total_cracks : 15
  const currentPhase = crisisData ? crisisData.current_phase : 1
  const crisisLevel = crisisData ? crisisData.crisis_level : 'Hidden Stress'
  const crisisColor = crisisData ? crisisData.crisis_color : '#fbbf24'
  const crisisProbability = crisisData ? crisisData.crisis_probability : 0

  // Calculate days until deadlines
  const lloydsUrgent = dashboard.countdowns.lloyds.days < 30
  const secUrgent = dashboard.countdowns.sec.days < 30

  return (
    <div className="hero-gradient">
      {/* Live Ticker Bar */}
      <div className="ticker-bar py-2">
        <div className="flex items-center justify-center gap-8 text-sm">
          <span className="flex items-center gap-2">
            <span className="live-dot" />
            <span className="text-gray-400">LIVE</span>
          </span>
          <span className="text-danger font-bold">
            Silver ${silver.price.toFixed(2)} ({silver.change_pct >= 0 ? '+' : ''}{silver.change_pct.toFixed(1)}%)
          </span>
          <span className="text-gray-500">|</span>
          <span className="text-warning">
            Bank Losses: ${(totalLoss / 1e9).toFixed(0)}B and counting
          </span>
          <span className="text-gray-500">|</span>
          <span className={cracksShowing > 0 ? 'text-danger' : 'text-gray-400'}>
            {cracksShowing} of {totalCracks} Crisis Indicators Active
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
          {/* Left: Silver Price & Move */}
          <motion.div
            className="text-center lg:text-left"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="text-xs uppercase tracking-widest text-gray-500 mb-1">The Trigger</div>
            <div className="text-6xl font-black text-white mb-2">${silver.price.toFixed(2)}</div>
            <div className="text-xl text-gray-400">
              Silver Spot Price
              <span className={`ml-3 font-bold ${silver.change_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                {silver.change_pct >= 0 ? '+' : ''}{silver.change_pct.toFixed(2)}%
              </span>
            </div>
            <div className="mt-4 p-3 rounded-lg bg-danger/10 border border-danger/20">
              <div className="text-xs text-gray-500 uppercase">Move from $30 Base</div>
              <div className="text-3xl font-black text-danger">+${silverMove.toFixed(2)}</div>
              <div className="text-xs text-gray-400 mt-1">Every $1 = $212M+ in bank losses</div>
            </div>
          </motion.div>

          {/* Center: Crisis Gauge Ring */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="relative inline-block">
              <svg width="220" height="220" viewBox="0 0 220 220" className="crisis-ring">
                {/* Background ring */}
                <circle cx="110" cy="110" r="90" fill="none" stroke="#1a1a1a" strokeWidth="12" />
                {/* Progress ring */}
                <circle
                  cx="110" cy="110" r="90"
                  fill="none"
                  stroke={crisisColor}
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${crisisProbability * 5.65} 565`}
                  transform="rotate(-90 110 110)"
                  className="transition-all duration-1000"
                />
                {/* Crack indicators */}
                {[...Array(totalCracks)].map((_, i) => {
                  const angle = (i / totalCracks) * 360 - 90
                  const rad = (angle * Math.PI) / 180
                  const x = 110 + 75 * Math.cos(rad)
                  const y = 110 + 75 * Math.sin(rad)
                  const isActive = i < cracksShowing
                  return (
                    <circle
                      key={i}
                      cx={x} cy={y} r="4"
                      fill={isActive ? '#dc2626' : '#333'}
                      className={isActive ? 'animate-pulse' : ''}
                    />
                  )
                })}
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-5xl font-black" style={{ color: crisisColor }}>
                  {crisisProbability.toFixed(0)}%
                </div>
                <div className="text-xs uppercase tracking-wider text-gray-500 mt-1">Crisis Risk</div>
              </div>
            </div>
            <div className="mt-4">
              <span className="badge" style={{ backgroundColor: `${crisisColor}20`, color: crisisColor, borderColor: `${crisisColor}50` }}>
                Phase {currentPhase}: {crisisLevel}
              </span>
            </div>
          </motion.div>

          {/* Right: Loss Counter & Deadlines */}
          <motion.div
            className="text-center lg:text-right"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="text-xs uppercase tracking-widest text-gray-500 mb-1">The Damage</div>
            <div className="text-5xl font-black text-danger glow-danger loss-counter">
              ${(totalLoss / 1e9).toFixed(1)}B
            </div>
            <div className="text-lg text-gray-400">Aggregate Bank Losses</div>

            <div className="mt-6 space-y-3">
              <div className={`p-3 rounded-lg ${lloydsUrgent ? 'bg-danger/10 border border-danger/30' : 'bg-black/30 border border-border'}`}>
                <div className="text-xs text-gray-500 uppercase">Lloyd's Deadline</div>
                <div className={`text-2xl font-bold ${lloydsUrgent ? 'text-danger countdown-critical' : 'text-white'}`}>
                  {dashboard.countdowns.lloyds.days}d {dashboard.countdowns.lloyds.hours}h
                </div>
              </div>
              <div className={`p-3 rounded-lg ${secUrgent ? 'bg-danger/10 border border-danger/30' : 'bg-black/30 border border-border'}`}>
                <div className="text-xs text-gray-500 uppercase">SEC Deadline</div>
                <div className={`text-2xl font-bold ${secUrgent ? 'text-danger countdown-critical' : 'text-white'}`}>
                  {dashboard.countdowns.sec.days}d {dashboard.countdowns.sec.hours}h
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Phase Progress Bar */}
        <motion.div
          className="mt-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex items-center gap-2 mb-3">
            {[1, 2, 3, 4].map((phase) => (
              <div key={phase} className="flex-1">
                <div className={`h-2 rounded-full transition-all duration-500 ${
                  phase < currentPhase ? 'bg-danger' :
                  phase === currentPhase ? 'bg-warning' :
                  'bg-gray-800'
                }`} />
                <div className={`text-xs mt-1 ${phase === currentPhase ? 'text-warning font-bold' : 'text-gray-600'}`}>
                  {phase === 1 ? 'Hidden Stress' : phase === 2 ? 'Market Stress' : phase === 3 ? 'Liquidity Crisis' : 'Public Crisis'}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

// Section Header Component
// Crisis Scanner Section - Collapsible Module with 5-minute auto-refresh
function CrisisScannerSection() {
  const [isExpanded, setIsExpanded] = useState(false)

  // Fetch crisis scanner data with 5-minute refresh interval (300000ms)
  const { data: scannerData, isLoading, error, dataUpdatedAt } = useQuery({
    queryKey: ['crisis-scanner'],
    queryFn: api.getCrisisScanner,
    refetchInterval: 300000, // 5 minutes
    refetchIntervalInBackground: true, // Keep refreshing even when tab is not focused
    staleTime: 60000, // Consider data stale after 1 minute
  })

  // Format time until next refresh
  const getNextRefreshTime = () => {
    if (!dataUpdatedAt) return 'Loading...'
    const nextRefresh = new Date(dataUpdatedAt + 300000)
    const now = new Date()
    const diff = Math.max(0, Math.floor((nextRefresh.getTime() - now.getTime()) / 1000))
    const mins = Math.floor(diff / 60)
    const secs = diff % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-4">
      {/* Scanner Toggle Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 rounded-lg transition-all duration-300 hover:bg-amber-500/5"
        style={{
          background: 'linear-gradient(90deg, rgba(245,158,11,0.1) 0%, transparent 50%)',
          border: '1px solid rgba(245,158,11,0.2)',
          borderLeft: '4px solid #F59E0B'
        }}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
            <Radio className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold tracking-wider text-white">CRISIS SCANNER</h3>
              {scannerData && (
                <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  {scannerData.system_status.alert_level}
                </span>
              )}
              {isLoading && (
                <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-gray-500/20 text-gray-400 border border-gray-500/30">
                  LOADING...
                </span>
              )}
            </div>
            <p className="text-[10px] text-gray-500 mt-0.5">
              Advanced monitoring module - Bank surveillance, Fed facilities, Verified/Unverified claims
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {scannerData && (
            <>
              <span className="text-[10px] text-emerald-500 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                AUTO-REFRESH 5min
              </span>
              <span className="text-[10px] text-gray-600">
                Next: {getNextRefreshTime()}
              </span>
            </>
          )}
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-amber-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </div>
      </button>

      {/* Scanner Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-4 p-4 rounded-lg bg-black/40 border border-gray-800">
              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <div className="text-gray-400">Loading Crisis Scanner...</div>
                  </div>
                </div>
              )}
              {error && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center text-red-400">
                    <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                    <div>Failed to load Crisis Scanner</div>
                    <div className="text-xs text-gray-500 mt-1">Check API connection</div>
                  </div>
                </div>
              )}
              {scannerData && (
                <CrisisScanner data={scannerData as any} />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function SectionHeader({ title, subtitle, icon: Icon, flowFrom }: { title: string; subtitle: string; icon?: any; flowFrom?: string }) {
  return (
    <div className="section-header">
      {flowFrom && (
        <div className="flex items-center gap-2 mb-2 text-xs text-gray-500">
          <div className="flex items-center gap-1 px-2 py-1 bg-gray-800/50 rounded-full">
            <span className="text-yellow-500">↓</span>
            <span>{flowFrom}</span>
          </div>
          <div className="flex-1 border-t border-dashed border-gray-700"></div>
        </div>
      )}
      <div className="flex items-center gap-3">
        {Icon && <Icon className="w-5 h-5 text-danger" />}
        <div>
          <h2>{title}</h2>
          <p className="text-gray-400 text-sm mt-1">{subtitle}</p>
        </div>
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

  // Fetch global physical prices
  const { data: globalPhysical } = useQuery({
    queryKey: ['global-physical'],
    queryFn: api.getGlobalPhysical,
    refetchInterval: 60000 // Refresh every minute
  })

  const statusColors: Record<string, string> = {
    normal: '#10B981',
    elevated: '#F59E0B',
    critical: '#EF4444'
  }

  return (
    <motion.div
      className="card cursor-pointer"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Live Prices</h3>
        </div>
        <div className="flex items-center gap-2">
          <VerificationBadge status="verified" size="xs" source="Exchange" />
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] text-gray-500 uppercase">COMEX Silver (Paper)</span>
          <VerificationBadge status="verified" size="xs" source="SI=F" />
        </div>
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-black text-white">${silver.price.toFixed(2)}</span>
          <span className={`text-sm font-bold ${silver.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {silver.change_pct >= 0 ? '+' : ''}{silver.change_pct.toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Global Physical Prices */}
      {globalPhysical && (
        <div className="mb-4 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] text-amber-400 uppercase font-bold">Physical Silver (What People Pay)</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {/* Shanghai */}
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-gray-400">Shanghai</span>
              <div className="flex items-center gap-1">
                <span className="text-sm font-bold text-white">${globalPhysical.shanghai.price.toFixed(0)}</span>
                <span
                  className="text-[9px] font-bold"
                  style={{ color: statusColors[globalPhysical.shanghai.status] }}
                >
                  +{globalPhysical.shanghai.premium_pct.toFixed(0)}%
                </span>
              </div>
            </div>
            {/* Dubai */}
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-gray-400">Dubai</span>
              <div className="flex items-center gap-1">
                <span className="text-sm font-bold text-white">${globalPhysical.dubai.price.toFixed(0)}</span>
                <span
                  className="text-[9px] font-bold"
                  style={{ color: statusColors[globalPhysical.dubai.status] }}
                >
                  +{globalPhysical.dubai.premium_pct.toFixed(0)}%
                </span>
              </div>
            </div>
            {/* Tokyo */}
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-gray-400">Tokyo</span>
              <div className="flex items-center gap-1">
                <span className="text-sm font-bold text-white">${globalPhysical.tokyo.price.toFixed(0)}</span>
                <span
                  className="text-[9px] font-bold"
                  style={{ color: statusColors[globalPhysical.tokyo.status] }}
                >
                  +{globalPhysical.tokyo.premium_pct.toFixed(0)}%
                </span>
              </div>
            </div>
            {/* US Retail */}
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-gray-400">US Retail</span>
              <div className="flex items-center gap-1">
                <span className="text-sm font-bold text-white">${globalPhysical.us_retail.price.toFixed(0)}</span>
                <span
                  className="text-[9px] font-bold"
                  style={{ color: statusColors[globalPhysical.us_retail.status] }}
                >
                  +{globalPhysical.us_retail.premium_pct.toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-amber-500/10">
            <div className="text-[8px] text-amber-400/60">Premium = physical price above COMEX paper spot</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="flex items-center gap-1 mb-0.5">
            <span className="text-[9px] text-gray-500">Gold</span>
            <VerificationDot status="verified" size="sm" />
          </div>
          <div className="text-lg font-bold">${gold.price.toFixed(0)}</div>
          <div className={`text-xs ${gold.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {gold.change_pct >= 0 ? '+' : ''}{gold.change_pct.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1 mb-0.5">
            <span className="text-[9px] text-gray-500">VIX</span>
            <VerificationDot status="verified" size="sm" />
          </div>
          <div className="text-lg font-bold">{vix.price.toFixed(1)}</div>
          <div className={`text-xs ${vix.change_pct <= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {vix.change_pct >= 0 ? '+' : ''}{vix.change_pct.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1 mb-0.5">
            <span className="text-[9px] text-gray-500">MS</span>
            <VerificationDot status="verified" size="sm" />
          </div>
          <div className="text-lg font-bold">${ms.price.toFixed(0)}</div>
          <div className={`text-xs ${ms.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {ms.change_pct >= 0 ? '+' : ''}{ms.change_pct.toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-gray-800">
        <div className="text-[9px] text-gray-600">Source: COMEX SI=F, SGE, Regional Markets • Real-time</div>
      </div>
    </motion.div>
  )
}

function BankCard() {
  const { data: banks } = useQuery({ queryKey: ['banks'], queryFn: api.getBanks })

  const topBanks = banks?.filter(b => b.paper_loss && b.paper_loss > 0).slice(0, 3) || []

  return (
    <motion.div
      className="card cursor-pointer border-orange-500/20"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-orange-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Bank Exposure</h3>
        </div>
        <VerificationBadge status="rumored" size="xs" />
      </div>

      <div className="text-[9px] text-orange-400 bg-orange-500/10 px-2 py-1 rounded mb-3">
        Position sizes unconfirmed - based on market analysis & OCC derivatives data
      </div>

      <div className="space-y-3">
        {topBanks.map((bank) => {
          const lossRatio = bank.paper_loss! / bank.equity
          const isInsolvent = lossRatio > 1

          return (
            <div key={bank.ticker}>
              <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{bank.name}</span>
                  <VerificationDot status="rumored" size="sm" />
                </div>
                <span className="text-sm text-red-400 font-bold">
                  {formatNumber(bank.paper_loss!)}
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-500 rounded-full transition-all"
                  style={{ width: `${Math.min(lossRatio * 100, 100)}%` }}
                />
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-[9px] text-gray-500">vs ${(bank.equity / 1e9).toFixed(0)}B equity</span>
                {isInsolvent && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-red-500/20 text-red-400 rounded">INSOLVENT</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-3 pt-2 border-t border-gray-800">
        <div className="text-[9px] text-gray-600">Based on: OCC Derivatives Reports, Market Analysis</div>
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

function AlertsCard({ alerts }: { alerts: AlertData[] }) {
  // Filter to only show VERIFIED alerts in the main alert card
  const verifiedAlerts = alerts.filter(a =>
    a.verification_status === 'verified' && !a.is_hypothetical
  )
  const criticalCount = verifiedAlerts.filter(a => a.level === 'critical').length

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
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Verified Alerts</h3>
        <VerificationBadge status="verified" size="sm" showLabel={false} />
        {criticalCount > 0 && (
          <span className="badge badge-danger ml-auto">{criticalCount}</span>
        )}
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {verifiedAlerts.length === 0 ? (
          <div className="text-center py-4 text-success">
            <span className="text-2xl">✓</span>
            <div className="text-sm mt-1">No verified alerts</div>
            <div className="text-xs text-gray-500 mt-1">All systems nominal</div>
          </div>
        ) : (
          verifiedAlerts.slice(0, 5).map((alert, i) => (
            <div
              key={i}
              className={`p-2 rounded text-sm ${
                alert.level === 'critical' ? 'bg-danger/10 border-l-2 border-danger' :
                alert.level === 'warning' ? 'bg-warning/10 border-l-2 border-warning' :
                'bg-info/10 border-l-2 border-info'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="font-semibold">{alert.title}</div>
                <VerificationBadge
                  status={alert.verification_status}
                  sourceCount={alert.source_count}
                  size="sm"
                />
              </div>
              <div className="text-xs text-gray-400">{alert.detail}</div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}

function WorkingTheoriesCard() {
  const { data: theories } = useQuery({ queryKey: ['theories'], queryFn: api.getTheories })

  return (
    <motion.div
      className="card cursor-pointer bg-orange-900/10 border-orange-500/30"
      whileHover={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.45 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <span className="text-orange-400 text-lg">?</span>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-orange-400">Working Theories</h3>
        <VerificationBadge status="theory" size="sm" showLabel={false} />
        <span className="text-xs text-orange-400/60 ml-auto">(Not Verified)</span>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {!theories || theories.length === 0 ? (
          <div className="text-center py-4 text-gray-500">
            <div className="text-sm">No active theories</div>
          </div>
        ) : (
          theories.slice(0, 3).map((theory) => (
            <div
              key={theory.id}
              className="p-2 rounded text-sm bg-gray-800/50 border border-orange-500/20"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-orange-300">{theory.title}</span>
                <span className="text-xs text-orange-400">{theory.confidence}%</span>
              </div>
              <div className="text-xs text-gray-400 line-clamp-2">{theory.hypothesis}</div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}

function TheoriesDetailView() {
  const { data: theories } = useQuery({ queryKey: ['theories'], queryFn: api.getTheories })

  return (
    <div className="space-y-4">
      <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 text-orange-400 font-semibold mb-2">
          <span>?</span> Important Disclaimer
        </div>
        <p className="text-gray-400 text-sm">
          These are <strong className="text-orange-300">working theories</strong> - hypotheses based on historical patterns,
          industry analysis, and unconfirmed reports. They are <strong className="text-orange-300">NOT verified facts</strong>.
          Always do your own research before making any decisions.
        </p>
      </div>

      {!theories || theories.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <span className="text-6xl">?</span>
          <div className="text-xl mt-4">No Working Theories</div>
          <div className="text-gray-400 mt-2">Check back for developing hypotheses</div>
        </div>
      ) : (
        <div className="space-y-4">
          {theories.map((theory) => (
            <div
              key={theory.id}
              className="p-4 rounded-lg bg-orange-900/10 border border-orange-500/30"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-orange-300">{theory.title}</span>
                  <VerificationBadge status={theory.status} size="sm" />
                </div>
                <div className="text-sm">
                  <span className="text-gray-500">Confidence: </span>
                  <span className={`font-semibold ${
                    theory.confidence >= 70 ? 'text-green-400' :
                    theory.confidence >= 50 ? 'text-yellow-400' :
                    'text-orange-400'
                  }`}>
                    {theory.confidence}%
                  </span>
                </div>
              </div>

              <p className="text-gray-300 mb-3">{theory.hypothesis}</p>

              <div className="space-y-2">
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider">Basis:</span>
                  <ul className="mt-1 text-sm text-gray-400 list-disc list-inside">
                    {theory.basis.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                </div>

                {theory.trigger_conditions.length > 0 && (
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider">Trigger Conditions:</span>
                    <ul className="mt-1 text-sm text-orange-300/80 list-disc list-inside">
                      {theory.trigger_conditions.map((t, i) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {theory.sources.length > 0 && (
                  <div className="text-xs text-gray-500 pt-2 border-t border-gray-700">
                    Sources: {theory.sources.map(s => `${s.name} (Tier ${s.tier})`).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
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

function NakedShortsCard() {
  const { data: nakedShorts } = useQuery({ queryKey: ['naked-shorts'], queryFn: api.getNakedShorts, refetchInterval: 60000 })

  if (!nakedShorts) return null

  const positionColors: Record<string, string> = {
    SHORT: '#ef4444',
    LONG: '#22c55e'
  }

  return (
    <motion.div
      className="card cursor-pointer lg:col-span-2"
      whileHover={{ scale: 1.01 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.95 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Skull className="w-4 h-4 text-red-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Naked Short Analysis</h3>
        </div>
        <div className="flex items-center gap-2">
          <VerificationBadge status="calculated" size="xs" source="OCC/CME" />
          <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-bold border border-red-500/30">
            {nakedShorts.paper_to_physical_ratio}:1 RATIO
          </span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <div className="p-2 rounded bg-black/30 border border-gray-800">
          <div className="flex items-center gap-1 mb-1">
            <span className="text-[9px] text-gray-500">Total Shorts</span>
            <VerificationBadge status="estimated" size="xs" />
          </div>
          <div className="text-xl font-black text-red-400">{(nakedShorts.total_short_oz / 1e9).toFixed(1)}B oz</div>
        </div>
        <div className="p-2 rounded bg-black/30 border border-emerald-500/20">
          <div className="flex items-center gap-1 mb-1">
            <span className="text-[9px] text-gray-500">Physical Available</span>
            <VerificationBadge status="verified" size="xs" />
          </div>
          <div className="text-xl font-black text-amber-400">{(nakedShorts.available_physical_oz / 1e9).toFixed(0)}B oz</div>
        </div>
        <div className="p-2 rounded bg-black/30 border border-red-500/20">
          <div className="flex items-center gap-1 mb-1">
            <span className="text-[9px] text-gray-500">Paper:Physical</span>
            <VerificationBadge status="calculated" size="xs" />
          </div>
          <div className="text-xl font-black text-red-400">{nakedShorts.paper_to_physical_ratio}:1</div>
        </div>
        <div className="p-2 rounded bg-black/30 border border-gray-800">
          <div className="flex items-center gap-1 mb-1">
            <span className="text-[9px] text-gray-500">Years Production</span>
            <VerificationBadge status="calculated" size="xs" />
          </div>
          <div className="text-xl font-black text-amber-400">{nakedShorts.years_of_production} yrs</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-2 text-gray-500">Bank</th>
              <th className="text-center py-2 text-gray-500">Status</th>
              <th className="text-right py-2 text-gray-500">Position</th>
              <th className="text-right py-2 text-gray-500">Ounces</th>
              <th className="text-right py-2 text-gray-500">Deadline</th>
              <th className="text-right py-2 text-gray-500">@$80 Risk</th>
            </tr>
          </thead>
          <tbody>
            {nakedShorts.bank_positions.slice(0, 6).map((bank) => (
              <tr key={bank.ticker} className="border-b border-gray-800/50">
                <td className="py-2 font-medium">{bank.name}</td>
                <td className="py-2 text-center">
                  <VerificationBadge status={bank.name.includes('rumored') ? 'rumored' : 'estimated'} size="xs" showLabel={false} />
                </td>
                <td className="py-2 text-right">
                  <span style={{ color: positionColors[bank.position] }} className="font-bold">{bank.position}</span>
                </td>
                <td className="py-2 text-right font-medium">{(bank.ounces / 1e9).toFixed(2)}B</td>
                <td className="py-2 text-right text-gray-400">{bank.deadline || 'N/A'}</td>
                <td className="py-2 text-right">
                  {bank.loss_ratio_at_80 ? (
                    <span className={bank.loss_ratio_at_80 > 1 ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                      {bank.loss_ratio_at_80.toFixed(1)}x equity
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-bold">PROFIT</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-3 p-2 bg-danger/10 rounded text-xs text-center text-danger">
        {nakedShorts.verdict}
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
  const { userId, showRegistration, setShowRegistration, handleRegistered, requestAccess, hasAccess } = useUserAccess()

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
      {/* Minimal Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-4 h-12 flex items-center justify-between">
          <h1 className="text-lg font-black text-white tracking-tight">
            fault<span className="text-danger">.</span>watch
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="live-dot" />
              <span className="text-xs text-gray-500">LIVE DATA</span>
            </div>
            <div className="text-xs text-gray-600">
              {new Date(dashboard.last_updated).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      {/* Critical Alert Banner */}
      {dashboard.alerts.some(a => a.level === 'critical') && (
        <div className="bg-red-600 text-white py-3 px-4 text-center border-b border-red-500/50">
          <span className="inline-flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-bold">[BREAKING]</span>
            {dashboard.alerts.find(a => a.level === 'critical')?.title}
            <VerificationBadge
              status={dashboard.alerts.find(a => a.level === 'critical')?.verification_status || 'unverified'}
              size="xs"
            />
          </span>
        </div>
      )}

      {/* CEO-Level Executive Summary Dashboard */}
      <ExecutiveSummary dashboard={dashboard} />

      {/* Crisis Scanner Module - Industrial Control Center */}
      <CrisisScannerSection />

      {/* Main Content - Organized by Narrative */}
      <main className="max-w-7xl mx-auto px-4 py-6">

        {/* SECTION 1: THE TRIGGER */}
        <SectionHeader
          title="THE TRIGGER"
          subtitle="Silver price movement driving bank losses"
          icon={Zap}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          <div onClick={() => setExpandedCard('prices')}><PriceCard prices={dashboard.prices} /></div>
          <div onClick={() => setExpandedCard('comex')}><ComexCard /></div>
          <div onClick={() => setExpandedCard('scenarios')}><ScenarioCard /></div>
        </div>

        {/* SECTION 2: THE EXPOSURE */}
        <SectionHeader
          title="THE EXPOSURE"
          subtitle="Bank short positions and potential insolvency"
          icon={Skull}
          flowFrom="Rising silver prices create massive losses on bank short positions"
        />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-12">
          <div onClick={() => setExpandedCard('naked-shorts')} className="lg:col-span-2"><NakedShortsCard /></div>
          <div onClick={() => setExpandedCard('banks')}><BankCard /></div>
        </div>

        {/* SECTION 3: THE CRACKS */}
        <SectionHeader
          title="THE CRACKS"
          subtitle="Early warning indicators of systemic stress"
          icon={Activity}
          flowFrom="Bank losses trigger credit stress, margin calls, and early warning signals"
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          <div onClick={() => setExpandedCard('fault-watch-alerts')}><FaultWatchAlertsCard /></div>
          <div onClick={() => setExpandedCard('crisis-gauge')}><CrisisGaugeCard /></div>
          <div onClick={() => setExpandedCard('possible-outlook')}><PossibleOutlookCard /></div>
          <div onClick={() => setExpandedCard('contagion')}><ContagionCard /></div>
          <div onClick={() => setExpandedCard('alerts')}><AlertsCard alerts={dashboard.alerts} /></div>
          <div onClick={() => setExpandedCard('theories')}><WorkingTheoriesCard /></div>
          <div onClick={() => setExpandedCard('crisis-search-pad')}><CrisisSearchPadCard /></div>
          <div onClick={() => setExpandedCard('risk-matrix')}><RiskMatrixCard /></div>
        </div>

        {/* SECTION 3.5: ADMINISTRATIVE CONTROL */}
        <SectionHeader
          title="THE OVERRIDE"
          subtitle="Government intervention and administrative control signals"
          icon={Shield}
          flowFrom="When markets break, governments step in — tracking who controls supply"
        />
        <div className="grid grid-cols-1 gap-4 mb-12">
          <div onClick={() => setExpandedCard('government')}><GovernmentInterventionCard /></div>
        </div>

        {/* SECTION 4: THE FALLOUT */}
        <SectionHeader
          title="THE FALLOUT"
          subtitle="Sector contagion and investment opportunities"
          icon={TrendingDown}
          flowFrom="Systemic stress spreads to other sectors, creating risks and opportunities"
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          <div onClick={() => setExpandedCard('sectors')}><SectorsCard /></div>
          <div onClick={() => setExpandedCard('miners')}><MinersCard /></div>
          <div onClick={() => setExpandedCard('opportunities')} className="lg:col-span-2"><OpportunitiesCard /></div>
        </div>

        {/* COMMUNITY & FEEDBACK - Always visible */}
        <SectionHeader
          title="COMMUNITY & FEEDBACK"
          subtitle="Join the community and help us build a better app"
          icon={Radio}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          {/* Registration or Community Stats */}
          {!hasAccess ? (
            <UserRegistrationCard onRegistered={handleRegistered} userId={userId} />
          ) : (
            <CommunityStatsCard />
          )}

          {/* Feedback Card - Always visible */}
          <FeedbackCard userId={userId} />

          {/* Why Join / Benefits */}
          {!hasAccess ? (
            <div className="card bg-gradient-to-br from-blue-900/20 to-cyan-900/20 border-blue-500/30">
              <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                <span className="text-2xl">📊</span> Why Join?
              </h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Full access to detailed bank exposure analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Real-time crisis gauge deep dives</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Scenario modeling and price projections</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Investment opportunity breakdowns</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Shape the future of fault.watch</span>
                </li>
              </ul>
              <p className="mt-4 text-xs text-gray-500">
                Connect all your social accounts to join our cross-platform community!
              </p>
            </div>
          ) : (
            <div className="card bg-gradient-to-br from-emerald-900/20 to-green-900/20 border-emerald-500/30">
              <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                <span className="text-2xl">🎯</span> What's Next
              </h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Mobile app with push alerts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Real-time price alerts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Community discussion board</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Portfolio tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Your suggestions here!</span>
                </li>
              </ul>
              <p className="mt-4 text-xs text-gray-500">
                Use the feedback card to tell us what you want!
              </p>
            </div>
          )}
        </div>

        {/* Footer with Resources */}
        <div className="border-t border-border pt-8 mt-8 text-center">
          <p className="text-xs text-gray-600 mb-4">
            Data refreshes every 60 seconds. Click any card for detailed analysis.
          </p>
          <p className="text-xs text-gray-700">
            fault.watch - Real-time monitoring of systemic banking risk from precious metals short exposure
          </p>
        </div>
      </main>

      {/* Registration Modal */}
      <Modal isOpen={showRegistration} onClose={() => setShowRegistration(false)} title="Unlock Deep Dive Access">
        <UserRegistrationCard onRegistered={handleRegistered} userId={userId} />
      </Modal>

      {/* Detail Modals - Gated behind registration */}
      <Modal isOpen={expandedCard === 'prices'} onClose={() => setExpandedCard(null)} title="Live Prices">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <PricesDetailView prices={dashboard.prices} />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'possible-outlook'} onClose={() => setExpandedCard(null)} title="Possible Outlook - Controlled Demolition Thesis">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <PossibleOutlookDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'contagion'} onClose={() => setExpandedCard(null)} title="Contagion Risk Analysis">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <ContagionDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'banks'} onClose={() => setExpandedCard(null)} title="Bank Exposure">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <BanksDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'comex'} onClose={() => setExpandedCard(null)} title="COMEX Silver Inventory">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <ContagionDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'alerts'} onClose={() => setExpandedCard(null)} title="Verified Alerts">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <AlertsDetailView alerts={dashboard.alerts} />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'theories'} onClose={() => setExpandedCard(null)} title="Working Theories">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <TheoriesDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'scenarios'} onClose={() => setExpandedCard(null)} title="Silver Price Scenarios">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <ScenariosDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'sectors'} onClose={() => setExpandedCard(null)} title="Sector Contagion">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <SectorsDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'miners'} onClose={() => setExpandedCard(null)} title="Junior Silver Miners">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <MinersDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'crisis-gauge'} onClose={() => setExpandedCard(null)} title="Crisis Gauge - System Crack Monitor">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <CrisisGaugeDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'naked-shorts'} onClose={() => setExpandedCard(null)} title="Naked Short Analysis - 30:1 Paper to Physical">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <NakedShortsDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'opportunities'} onClose={() => setExpandedCard(null)} title="Investment Opportunities">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <OpportunitiesDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'government'} onClose={() => setExpandedCard(null)} title="Administrative Control Layer">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <GovernmentInterventionDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'fault-watch-alerts'} onClose={() => setExpandedCard(null)} title="Fault-Watch Strategic Alerts">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <FaultWatchAlertsDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'crisis-search-pad'} onClose={() => setExpandedCard(null)} title="Crisis Search Pad - Research & Monitoring">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <CrisisSearchPadDetailView />
        </AccessGate>
      </Modal>

      <Modal isOpen={expandedCard === 'risk-matrix'} onClose={() => setExpandedCard(null)} title="Risk Matrix - Event Impact Analysis">
        <AccessGate userId={userId} onRequestAccess={() => { setExpandedCard(null); requestAccess(); }}>
          <RiskMatrixDetailView />
        </AccessGate>
      </Modal>
    </div>
  )
}
