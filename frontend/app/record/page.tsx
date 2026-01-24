'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Clock,
  Skull,
  Target,
  Zap,
  Play,
  Pause,
  RotateCcw,
  ChevronDown
} from 'lucide-react'

// Data for recording
const SLIDES = [
  {
    id: 'price',
    type: 'hero',
    title: 'SILVER SPOT PRICE',
    value: '$103.92',
    subtitle: '+$1.01 (+0.98%)',
    positive: true,
    footer: 'January 24, 2026'
  },
  {
    id: 'insolvent',
    type: 'stat',
    icon: 'skull',
    title: 'BANKS INSOLVENT',
    value: '5 of 6',
    subtitle: 'Major global banks',
    description: 'At current silver prices, 5 banks have exceeded their Tier 1 capital in losses'
  },
  {
    id: 'wiped',
    type: 'stat',
    icon: 'alert',
    title: 'TIER 1 CAPITAL WIPED',
    value: '$657B+',
    subtitle: 'And counting',
    description: 'Combined bank capital destroyed by alleged short positions'
  },
  {
    id: 'countdown',
    type: 'countdown',
    title: 'NEXT DEADLINE',
    bank: 'HSBC',
    days: 7,
    date: 'January 31, 2026',
    description: 'Internal deadline to cover positions'
  },
  {
    id: 'positions',
    type: 'list',
    title: 'ALLEGED SHORT POSITIONS',
    items: [
      { bank: 'JPMorgan', amount: '7.95B oz', status: 'insolvent' },
      { bank: 'HSBC', amount: '7.30B oz', status: 'insolvent' },
      { bank: 'UBS', amount: '5.20B oz', status: 'insolvent' },
      { bank: 'Morgan Stanley', amount: '4.00B oz', status: 'insolvent' },
      { bank: 'Citigroup', amount: '3.40B oz', status: 'insolvent' },
      { bank: 'Bank of America', amount: '1.00B oz', status: 'solvent' },
    ]
  },
  {
    id: 'probability',
    type: 'gauge',
    title: 'CRISIS PROBABILITY',
    value: 72,
    description: 'Based on current market conditions and alleged positions'
  },
  {
    id: 'cta',
    type: 'cta',
    title: 'FAULT.WATCH',
    subtitle: 'Follow for daily updates',
    description: 'Link in bio for full analysis'
  }
]

export default function RecordPage() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [autoAdvance, setAutoAdvance] = useState(true)

  useEffect(() => {
    if (isPlaying && autoAdvance) {
      const timer = setTimeout(() => {
        if (currentSlide < SLIDES.length - 1) {
          setCurrentSlide(prev => prev + 1)
        } else {
          setIsPlaying(false)
        }
      }, 3000) // 3 seconds per slide

      return () => clearTimeout(timer)
    }
  }, [isPlaying, currentSlide, autoAdvance])

  const reset = () => {
    setCurrentSlide(0)
    setIsPlaying(false)
  }

  const togglePlay = () => {
    if (currentSlide >= SLIDES.length - 1) {
      setCurrentSlide(0)
    }
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex flex-col">
      {/* Controls - Hidden during recording, show on hover */}
      <div className="fixed top-4 left-4 right-4 z-50 flex justify-between items-center opacity-30 hover:opacity-100 transition-opacity">
        <div className="flex items-center gap-2">
          <button
            onClick={togglePlay}
            className="p-3 bg-gray-800 rounded-full hover:bg-gray-700"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={reset}
            className="p-3 bg-gray-800 rounded-full hover:bg-gray-700"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span>{currentSlide + 1} / {SLIDES.length}</span>
        </div>
      </div>

      {/* Progress Dots */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex gap-2">
        {SLIDES.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrentSlide(i)}
            className={`w-2 h-2 rounded-full transition-all ${
              i === currentSlide ? 'bg-red-500 w-6' : i < currentSlide ? 'bg-red-500/50' : 'bg-gray-600'
            }`}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlide}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-md"
          >
            <SlideContent slide={SLIDES[currentSlide]} />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Swipe Hint */}
      {currentSlide < SLIDES.length - 1 && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-500 animate-bounce">
          <ChevronDown className="w-6 h-6" />
          <span className="text-xs">Swipe or tap to continue</span>
        </div>
      )}

      {/* Tap Zones */}
      <div
        className="fixed inset-0 z-40 flex"
        onClick={(e) => {
          const x = e.clientX / window.innerWidth
          if (x < 0.3 && currentSlide > 0) {
            setCurrentSlide(prev => prev - 1)
          } else if (x > 0.7 && currentSlide < SLIDES.length - 1) {
            setCurrentSlide(prev => prev + 1)
          }
        }}
      />

      {/* Disclaimer */}
      <div className="fixed bottom-2 left-0 right-0 text-center text-[10px] text-gray-600 z-30">
        UNVERIFIED SPECULATIVE ANALYSIS - NOT FINANCIAL ADVICE
      </div>
    </div>
  )
}

function SlideContent({ slide }: { slide: typeof SLIDES[0] }) {
  switch (slide.type) {
    case 'hero':
      return (
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-red-500/20 text-red-400 px-4 py-2 rounded-full text-sm font-bold mb-6">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            LIVE
          </div>
          <h2 className="text-xl text-gray-400 uppercase tracking-wider mb-4">{slide.title}</h2>
          <div className="text-7xl md:text-8xl font-black mb-4">{slide.value}</div>
          <div className={`text-2xl font-bold flex items-center justify-center gap-2 ${slide.positive ? 'text-green-400' : 'text-red-400'}`}>
            {slide.positive ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
            {slide.subtitle}
          </div>
          <div className="mt-6 text-gray-500">{slide.footer}</div>
        </div>
      )

    case 'stat':
      return (
        <div className="text-center">
          <div className="mb-6">
            {slide.icon === 'skull' && <Skull className="w-16 h-16 mx-auto text-red-500" />}
            {slide.icon === 'alert' && <AlertTriangle className="w-16 h-16 mx-auto text-amber-500" />}
          </div>
          <h2 className="text-xl text-gray-400 uppercase tracking-wider mb-4">{slide.title}</h2>
          <div className="text-6xl md:text-7xl font-black text-red-400 mb-2">{slide.value}</div>
          <div className="text-xl text-gray-400">{slide.subtitle}</div>
          <div className="mt-6 text-sm text-gray-500 max-w-xs mx-auto">{slide.description}</div>
        </div>
      )

    case 'countdown':
      return (
        <div className="text-center">
          <Clock className="w-16 h-16 mx-auto text-purple-500 mb-6" />
          <h2 className="text-xl text-gray-400 uppercase tracking-wider mb-2">{slide.title}</h2>
          <div className="text-3xl font-bold text-white mb-6">{slide.bank}</div>
          <div className="text-8xl font-black text-purple-400 mb-2">{slide.days}</div>
          <div className="text-2xl text-gray-400">DAYS</div>
          <div className="mt-6 text-gray-500">{slide.date}</div>
          <div className="mt-2 text-sm text-gray-600">{slide.description}</div>
        </div>
      )

    case 'list':
      return (
        <div>
          <h2 className="text-xl text-gray-400 uppercase tracking-wider text-center mb-6">{slide.title}</h2>
          <div className="space-y-3">
            {slide.items?.map((item, i) => (
              <motion.div
                key={item.bank}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`flex items-center justify-between p-4 rounded-xl ${
                  item.status === 'insolvent' ? 'bg-red-500/10 border border-red-500/30' : 'bg-green-500/10 border border-green-500/30'
                }`}
              >
                <span className="font-bold">{item.bank}</span>
                <div className="flex items-center gap-3">
                  <span className="text-gray-400">{item.amount}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    item.status === 'insolvent' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
                  }`}>
                    {item.status.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )

    case 'gauge':
      const gaugeValue = typeof slide.value === 'number' ? slide.value : 0
      return (
        <div className="text-center">
          <Target className="w-16 h-16 mx-auto text-blue-500 mb-6" />
          <h2 className="text-xl text-gray-400 uppercase tracking-wider mb-8">{slide.title}</h2>
          <div className="relative w-64 h-64 mx-auto">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="#1f2937"
                strokeWidth="10"
              />
              <motion.circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={`${gaugeValue * 2.83} 283`}
                initial={{ strokeDasharray: '0 283' }}
                animate={{ strokeDasharray: `${gaugeValue * 2.83} 283` }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#ef4444" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-5xl font-black">{slide.value}%</span>
            </div>
          </div>
          <div className="mt-6 text-sm text-gray-500 max-w-xs mx-auto">{slide.description}</div>
        </div>
      )

    case 'cta':
      return (
        <div className="text-center">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Zap className="w-20 h-20 mx-auto text-red-500 mb-6" />
          </motion.div>
          <h1 className="text-4xl font-black mb-4">{slide.title}</h1>
          <div className="text-xl text-gray-400 mb-2">{slide.subtitle}</div>
          <div className="text-gray-500">{slide.description}</div>
          <div className="mt-8 inline-flex items-center gap-2 bg-red-500 text-white px-6 py-3 rounded-full font-bold">
            <span>FOLLOW FOR UPDATES</span>
          </div>
        </div>
      )

    default:
      return null
  }
}
