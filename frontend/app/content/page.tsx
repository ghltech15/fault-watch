'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import html2canvas from 'html2canvas'
import Link from 'next/link'
import {
  Camera,
  Download,
  Share2,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Clock,
  Skull,
  Target,
  Zap,
  ArrowLeft,
  Smartphone,
  Monitor,
  RefreshCw,
  Copy,
  Check
} from 'lucide-react'

// Simulated daily data - in production this would come from API
const TODAYS_DATA = {
  date: 'January 24, 2026',
  silverPrice: 103.92,
  silverChange: +1.01,
  silverChangePercent: +0.98,
  previousClose: 102.91,
  banksInsolvent: 5,
  totalBanks: 6,
  tier1Wiped: 657,
  daysToFirstDeadline: 7,
  nextDeadline: 'HSBC - Jan 31',
  crisisProbability: 72,
  changes: [
    { item: 'Silver Price', from: '$102.91', to: '$103.92', direction: 'up' as const },
    { item: 'UBS Days to Exhaustion', from: '2-3 days', to: '1-2 days', direction: 'down' as const },
    { item: 'Crisis Probability', from: '70%', to: '72%', direction: 'up' as const },
    { item: 'HSBC Countdown', from: '8 days', to: '7 days', direction: 'down' as const },
  ]
}

export default function ContentCreatorPage() {
  const [view, setView] = useState<'vertical' | 'square' | 'horizontal'>('vertical')
  const [capturing, setCapturing] = useState(false)
  const [copied, setCopied] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)
  const [currentTime, setCurrentTime] = useState('')

  useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString())
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const captureScreenshot = async () => {
    if (!cardRef.current) return
    setCapturing(true)

    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#0a0a0f',
        scale: 2,
        logging: false,
        useCORS: true,
      })

      const link = document.createElement('a')
      link.download = `faultwatch-${TODAYS_DATA.date.replace(/,?\s+/g, '-').toLowerCase()}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    } catch (err) {
      console.error('Screenshot failed:', err)
    }

    setCapturing(false)
  }

  const copyStats = () => {
    const stats = `FAULT.WATCH Daily Update - ${TODAYS_DATA.date}

Silver: $${TODAYS_DATA.silverPrice.toFixed(2)} (${TODAYS_DATA.silverChange >= 0 ? '+' : ''}${TODAYS_DATA.silverChangePercent.toFixed(2)}%)
Banks Insolvent: ${TODAYS_DATA.banksInsolvent}/${TODAYS_DATA.totalBanks}
Tier 1 Capital Wiped: $${TODAYS_DATA.tier1Wiped}B+
Crisis Probability: ${TODAYS_DATA.crisisProbability}%
Next Deadline: ${TODAYS_DATA.nextDeadline} (${TODAYS_DATA.daysToFirstDeadline} days)

Full analysis: fault.watch

#silver #banks #financialcrisis #faultwatch`

    navigator.clipboard.writeText(stats)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const viewSizes = {
    vertical: 'w-[390px] min-h-[844px]',
    square: 'w-[500px] h-[500px]',
    horizontal: 'w-[800px] h-[450px]'
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#0a0a0f]/95 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white">
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </Link>
          <h1 className="text-xl font-bold">Content Creator Tools</h1>
          <div className="text-sm text-gray-400">{currentTime}</div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          {/* View Selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Format:</span>
            <div className="flex rounded-lg border border-gray-700 overflow-hidden">
              <button
                onClick={() => setView('vertical')}
                className={`px-4 py-2 flex items-center gap-2 text-sm ${view === 'vertical' ? 'bg-red-500 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
              >
                <Smartphone className="w-4 h-4" />
                TikTok (9:16)
              </button>
              <button
                onClick={() => setView('square')}
                className={`px-4 py-2 flex items-center gap-2 text-sm ${view === 'square' ? 'bg-red-500 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
              >
                <Monitor className="w-4 h-4" />
                Instagram (1:1)
              </button>
              <button
                onClick={() => setView('horizontal')}
                className={`px-4 py-2 flex items-center gap-2 text-sm ${view === 'horizontal' ? 'bg-red-500 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
              >
                <Monitor className="w-4 h-4 rotate-90" />
                Twitter (16:9)
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={copyStats}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
            >
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied!' : 'Copy Caption'}
            </button>
            <button
              onClick={captureScreenshot}
              disabled={capturing}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-sm font-bold disabled:opacity-50"
            >
              {capturing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              {capturing ? 'Capturing...' : 'Download Image'}
            </button>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Preview Card */}
          <div className="flex-1 flex justify-center">
            <div
              ref={cardRef}
              className={`${viewSizes[view]} bg-gradient-to-br from-[#0a0a0f] via-[#0f1419] to-[#0a0a0f] rounded-3xl overflow-hidden border border-gray-800 shadow-2xl`}
            >
              {view === 'vertical' ? (
                <VerticalCard data={TODAYS_DATA} />
              ) : view === 'square' ? (
                <SquareCard data={TODAYS_DATA} />
              ) : (
                <HorizontalCard data={TODAYS_DATA} />
              )}
            </div>
          </div>

          {/* What Changed Today */}
          <div className="lg:w-80">
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-amber-400" />
                What Changed Today
              </h3>
              <div className="space-y-3">
                {TODAYS_DATA.changes.map((change, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <span className="text-sm text-gray-400">{change.item}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">{change.from}</span>
                      <span className="text-gray-600">→</span>
                      <span className={`text-sm font-bold ${change.direction === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                        {change.to}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <h4 className="font-bold mb-3">Quick Hooks</h4>
                <div className="space-y-2 text-sm">
                  <div className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800">
                    "Silver just crossed $104 - {TODAYS_DATA.banksInsolvent} banks are now insolvent"
                  </div>
                  <div className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800">
                    "{TODAYS_DATA.daysToFirstDeadline} days until {TODAYS_DATA.nextDeadline.split(' - ')[0]}'s deadline"
                  </div>
                  <div className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800">
                    "${TODAYS_DATA.tier1Wiped} BILLION in bank capital wiped out"
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <TipCard
            icon={<Camera className="w-6 h-6" />}
            title="Screen Record"
            description="Open fault.watch/crisis-dashboard on your phone, hit record, and slowly scroll through the data"
          />
          <TipCard
            icon={<Zap className="w-6 h-6" />}
            title="Strong Hook"
            description="Start with the most dramatic stat: price, insolvency count, or countdown days"
          />
          <TipCard
            icon={<Share2 className="w-6 h-6" />}
            title="Call to Action"
            description="End with 'Follow for daily updates' and 'Link in bio for full analysis'"
          />
        </div>
      </div>
    </div>
  )
}

// Vertical Card (TikTok/Reels format)
function VerticalCard({ data }: { data: typeof TODAYS_DATA }) {
  return (
    <div className="h-full flex flex-col p-6">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-xs font-bold mb-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          LIVE UPDATE
        </div>
        <h1 className="text-2xl font-black">FAULT.WATCH</h1>
        <p className="text-xs text-gray-500">{data.date}</p>
      </div>

      {/* Silver Price - Hero */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 mb-4 border border-gray-700">
        <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Silver Spot Price</div>
        <div className="text-5xl font-black text-white mb-2">${data.silverPrice.toFixed(2)}</div>
        <div className={`text-xl font-bold flex items-center gap-1 ${data.silverChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {data.silverChange >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          {data.silverChange >= 0 ? '+' : ''}{data.silverChangePercent.toFixed(2)}%
        </div>
      </div>

      {/* Crisis Stats */}
      <div className="flex-1 space-y-3">
        <StatRow
          icon={<Skull className="w-5 h-5 text-red-400" />}
          label="Banks Insolvent"
          value={`${data.banksInsolvent} of ${data.totalBanks}`}
          highlight
        />
        <StatRow
          icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
          label="Tier 1 Capital Wiped"
          value={`$${data.tier1Wiped}B+`}
        />
        <StatRow
          icon={<Target className="w-5 h-5 text-blue-400" />}
          label="Crisis Probability"
          value={`${data.crisisProbability}%`}
        />
        <StatRow
          icon={<Clock className="w-5 h-5 text-purple-400" />}
          label={`${data.nextDeadline.split(' - ')[0]} Deadline`}
          value={`${data.daysToFirstDeadline} days`}
          countdown
        />
      </div>

      {/* Countdown Bar */}
      <div className="mt-4 bg-red-500/20 rounded-xl p-4 border border-red-500/30">
        <div className="text-center">
          <div className="text-4xl font-black text-red-400">{data.daysToFirstDeadline}</div>
          <div className="text-xs text-gray-400">DAYS TO {data.nextDeadline.split(' - ')[0].toUpperCase()}</div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 text-center">
        <div className="text-xs text-gray-500">UNVERIFIED ANALYSIS - NOT FINANCIAL ADVICE</div>
        <div className="text-sm font-bold text-gray-400 mt-1">fault.watch</div>
      </div>
    </div>
  )
}

// Square Card (Instagram format)
function SquareCard({ data }: { data: typeof TODAYS_DATA }) {
  return (
    <div className="h-full flex flex-col p-6 justify-between">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black">FAULT.WATCH</h1>
          <p className="text-xs text-gray-500">{data.date}</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-black">${data.silverPrice.toFixed(2)}</div>
          <div className={`text-sm font-bold ${data.silverChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.silverChange >= 0 ? '+' : ''}{data.silverChangePercent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <BigStat label="Banks Insolvent" value={`${data.banksInsolvent}/${data.totalBanks}`} color="red" />
        <BigStat label="Capital Wiped" value={`$${data.tier1Wiped}B`} color="amber" />
        <BigStat label="Crisis Prob" value={`${data.crisisProbability}%`} color="blue" />
        <BigStat label="Days to Deadline" value={`${data.daysToFirstDeadline}`} color="purple" />
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-gray-500">
        UNVERIFIED ANALYSIS | fault.watch
      </div>
    </div>
  )
}

// Horizontal Card (Twitter format)
function HorizontalCard({ data }: { data: typeof TODAYS_DATA }) {
  return (
    <div className="h-full flex p-6">
      {/* Left Side - Price */}
      <div className="w-1/3 flex flex-col justify-center border-r border-gray-700 pr-6">
        <h1 className="text-xl font-black mb-1">FAULT.WATCH</h1>
        <p className="text-xs text-gray-500 mb-4">{data.date}</p>
        <div className="text-4xl font-black">${data.silverPrice.toFixed(2)}</div>
        <div className={`text-lg font-bold ${data.silverChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {data.silverChange >= 0 ? '+' : ''}{data.silverChangePercent.toFixed(2)}%
        </div>
      </div>

      {/* Right Side - Stats */}
      <div className="flex-1 pl-6 flex flex-col justify-center">
        <div className="grid grid-cols-2 gap-4">
          <MiniStat label="Banks Insolvent" value={`${data.banksInsolvent}/${data.totalBanks}`} />
          <MiniStat label="Tier 1 Wiped" value={`$${data.tier1Wiped}B+`} />
          <MiniStat label="Crisis Probability" value={`${data.crisisProbability}%`} />
          <MiniStat label={`${data.nextDeadline.split(' - ')[0]} Deadline`} value={`${data.daysToFirstDeadline} days`} />
        </div>
        <div className="mt-4 text-xs text-gray-500">UNVERIFIED ANALYSIS - NOT FINANCIAL ADVICE</div>
      </div>
    </div>
  )
}

function StatRow({ icon, label, value, highlight, countdown }: {
  icon: React.ReactNode
  label: string
  value: string
  highlight?: boolean
  countdown?: boolean
}) {
  return (
    <div className={`flex items-center justify-between p-3 rounded-xl ${highlight ? 'bg-red-500/20 border border-red-500/30' : 'bg-gray-800/50'}`}>
      <div className="flex items-center gap-3">
        {icon}
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <span className={`font-bold ${highlight ? 'text-red-400' : countdown ? 'text-purple-400' : 'text-white'}`}>
        {value}
      </span>
    </div>
  )
}

function BigStat({ label, value, color }: { label: string; value: string; color: 'red' | 'amber' | 'blue' | 'purple' }) {
  const colors = {
    red: 'bg-red-500/20 border-red-500/30 text-red-400',
    amber: 'bg-amber-500/20 border-amber-500/30 text-amber-400',
    blue: 'bg-blue-500/20 border-blue-500/30 text-blue-400',
    purple: 'bg-purple-500/20 border-purple-500/30 text-purple-400',
  }

  return (
    <div className={`${colors[color]} border rounded-xl p-4 text-center`}>
      <div className="text-3xl font-black">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{label}</div>
    </div>
  )
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  )
}

function TipCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
      <div className="text-red-400 mb-3">{icon}</div>
      <h3 className="font-bold mb-2">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  )
}
