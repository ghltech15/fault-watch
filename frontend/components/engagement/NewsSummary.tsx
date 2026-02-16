'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Flag, FileText, BarChart3, ArrowRight, AlertTriangle, Clock, TrendingUp, Activity, Share2 } from 'lucide-react'

interface NewsItem {
  id: string
  title: string
  summary: string
  link: string
  icon: React.ReactNode
  category: 'analysis' | 'report' | 'alert'
  isNew?: boolean
  date: string
}

interface RiskScanData {
  timestamp: string
  headline: string
  summary: string
  direction: 'rising' | 'falling' | 'stable'
  severity: string
  silverPrice: number
  silverChange: number
  phase: number
  cracksShowing: number
  formattedDate: string
}

const NEWS_ITEMS: NewsItem[] = [
  {
    id: 'trump-eo',
    title: 'Trump Executive Orders & The Silver Crisis Matrix',
    summary: '230+ executive orders analyzed reveal potential pattern of positioning for major monetary/financial system restructuring that converges with the alleged silver short squeeze timeline.',
    link: '/trump-eo-analysis',
    icon: <Flag className="w-5 h-5" />,
    category: 'analysis',
    isNew: true,
    date: 'Jan 24, 2026'
  },
  {
    id: 'deep-dive',
    title: 'The Silver Short Apocalypse - Full Report',
    summary: '28.85 billion oz alleged short positions across 6 major banks. 5 of 6 technically insolvent at current prices. Complete insolvency analysis and cascade timeline.',
    link: '/deep-dive',
    icon: <FileText className="w-5 h-5" />,
    category: 'report',
    date: 'Jan 23, 2026'
  },
  {
    id: 'crisis-dashboard',
    title: 'Real-Time Crisis Monitoring Dashboard',
    summary: 'Live tracking of bank insolvency status, countdown timers to regulatory deadlines, and projected cascade timeline with price targets.',
    link: '/crisis-dashboard',
    icon: <BarChart3 className="w-5 h-5" />,
    category: 'report',
    date: 'Live'
  }
]

export function NewsSummary() {
  const [riskScan, setRiskScan] = useState<RiskScanData | null>(null)

  // Fetch daily risk scan
  useEffect(() => {
    fetch('/api/risk-scan')
      .then(res => res.json())
      .then(data => setRiskScan(data))
      .catch(err => console.error('Failed to fetch risk scan:', err))
  }, [])

  const handleShareDailyScan = () => {
    if (!riskScan) return
    const text = `${riskScan.headline} | fault.watch`
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank')
  }

  return (
    <section className="max-w-6xl mx-auto px-4 py-8">
      {/* Daily Systemic Risk Scan - Pinned */}
      {riskScan && (
        <motion.div
          className={`mb-6 p-5 rounded-xl border ${
            riskScan.direction === 'rising' ? 'bg-red-500/5 border-red-500/30' :
            riskScan.direction === 'falling' ? 'bg-green-500/5 border-green-500/30' :
            'bg-gray-500/5 border-gray-500/30'
          }`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${
                riskScan.direction === 'rising' ? 'bg-red-500/20' :
                riskScan.direction === 'falling' ? 'bg-green-500/20' :
                'bg-gray-500/20'
              }`}>
                <Activity className={`w-5 h-5 ${
                  riskScan.direction === 'rising' ? 'text-red-400' :
                  riskScan.direction === 'falling' ? 'text-green-400' :
                  'text-gray-400'
                }`} />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-[var(--text-primary)]">Daily Systemic Risk Scan</h3>
                  <span className="text-xs text-[var(--text-muted)]">{riskScan.formattedDate}</span>
                </div>
                <p className={`text-sm font-medium ${
                  riskScan.direction === 'rising' ? 'text-red-400' :
                  riskScan.direction === 'falling' ? 'text-green-400' :
                  'text-gray-400'
                }`}>
                  {riskScan.headline}
                </p>
                <p className="text-sm text-[var(--text-secondary)] mt-2">
                  {riskScan.summary}
                </p>
              </div>
            </div>
            <button
              onClick={handleShareDailyScan}
              className="flex-shrink-0 p-2 rounded-lg hover:bg-white/5 transition-colors"
              title="Share on Twitter"
            >
              <Share2 className="w-4 h-4 text-gray-400 hover:text-blue-400" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Section Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[var(--text-primary)]">Latest Analysis</h2>
            <p className="text-sm text-[var(--text-muted)]">Unverified speculative reports - not financial advice</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-amber-400 text-xs">
          <AlertTriangle className="w-4 h-4" />
          <span className="hidden sm:inline">All content unverified</span>
        </div>
      </div>

      {/* News Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        {NEWS_ITEMS.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Link href={item.link} className="block group">
              <div className={`relative h-full bg-[var(--bg-secondary)] border rounded-xl p-5 transition-all hover:border-blue-500/50 hover:bg-blue-500/5 ${
                item.isNew ? 'border-blue-500/30' : 'border-[var(--border-primary)]'
              }`}>
                {/* New Badge */}
                {item.isNew && (
                  <div className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs font-bold px-2 py-0.5 rounded-full animate-pulse">
                    NEW
                  </div>
                )}

                {/* Header */}
                <div className="flex items-start gap-3 mb-3">
                  <div className={`p-2 rounded-lg ${
                    item.category === 'analysis' ? 'bg-blue-500/20 text-blue-400' :
                    item.category === 'alert' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {item.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-[var(--text-primary)] text-sm leading-tight group-hover:text-blue-400 transition-colors line-clamp-2">
                      {item.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Clock className="w-3 h-3 text-[var(--text-muted)]" />
                      <span className="text-xs text-[var(--text-muted)]">{item.date}</span>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-sm text-[var(--text-secondary)] line-clamp-3 mb-4">
                  {item.summary}
                </p>

                {/* Read More */}
                <div className="flex items-center gap-1 text-blue-400 text-sm font-medium group-hover:gap-2 transition-all">
                  <span>Read more</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Disclaimer */}
      <p className="text-center text-xs text-[var(--text-muted)] mt-4">
        All reports are speculative analysis exploring possible scenarios. Not investment advice. Always do your own research.
      </p>
    </section>
  )
}
