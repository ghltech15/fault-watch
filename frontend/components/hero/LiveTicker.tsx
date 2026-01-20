'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle } from 'lucide-react'

interface TickerItem {
  label: string
  value: string
  change?: number
  verified?: boolean
  alert?: boolean
}

interface LiveTickerProps {
  items: TickerItem[]
}

export function LiveTicker({ items }: LiveTickerProps) {
  // Duplicate items for seamless loop
  const allItems = [...items, ...items]

  return (
    <div className="relative overflow-hidden bg-black/50 border-y border-gray-800 py-3">
      {/* Fade edges */}
      <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-black to-transparent z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-black to-transparent z-10" />

      {/* Live indicator */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 flex items-center gap-2">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </span>
        <span className="text-[10px] font-bold text-green-400 uppercase tracking-wider">LIVE</span>
      </div>

      {/* Scrolling content */}
      <motion.div
        className="flex items-center gap-8 whitespace-nowrap pl-24"
        animate={{ x: [0, -50 * items.length + '%'] }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: 'loop',
            duration: items.length * 5,
            ease: 'linear'
          }
        }}
      >
        {allItems.map((item, index) => (
          <div key={index} className="flex items-center gap-3">
            {/* Separator */}
            {index > 0 && <span className="text-gray-700 mx-2">|</span>}

            {/* Alert icon if needed */}
            {item.alert && <AlertTriangle className="w-4 h-4 text-amber-400" />}

            {/* Label */}
            <span className="text-gray-400 text-sm font-medium">{item.label}</span>

            {/* Value */}
            <span className="text-white text-sm font-bold">{item.value}</span>

            {/* Change indicator */}
            {item.change !== undefined && (
              <span
                className={`flex items-center gap-1 text-sm font-bold ${
                  item.change > 0
                    ? 'text-green-400'
                    : item.change < 0
                    ? 'text-red-400'
                    : 'text-gray-400'
                }`}
              >
                {item.change > 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : item.change < 0 ? (
                  <TrendingDown className="w-3 h-3" />
                ) : (
                  <Minus className="w-3 h-3" />
                )}
                {item.change > 0 ? '+' : ''}
                {item.change.toFixed(2)}%
              </span>
            )}

            {/* Verified badge */}
            {item.verified && (
              <CheckCircle className="w-3 h-3 text-emerald-400" />
            )}
          </div>
        ))}
      </motion.div>
    </div>
  )
}
