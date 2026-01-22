'use client'

import { useMemo } from 'react'
import { motion } from 'framer-motion'

interface SparklineProps {
  data: number[]
  width?: number
  height?: number
  color?: string
  showArea?: boolean
  showDots?: boolean
  animated?: boolean
}

export function Sparkline({
  data,
  width = 100,
  height = 30,
  color = '#f59e0b',
  showArea = true,
  showDots = false,
  animated = true
}: SparklineProps) {
  const { path, areaPath, points, min, max, lastValue, firstValue } = useMemo(() => {
    if (!data || data.length === 0) {
      return { path: '', areaPath: '', points: [], min: 0, max: 0, lastValue: 0, firstValue: 0 }
    }

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    const padding = 2
    const effectiveWidth = width - padding * 2
    const effectiveHeight = height - padding * 2

    const points = data.map((value, index) => ({
      x: padding + (index / (data.length - 1)) * effectiveWidth,
      y: padding + effectiveHeight - ((value - min) / range) * effectiveHeight,
      value
    }))

    // Create SVG path
    const path = points
      .map((point, i) => `${i === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
      .join(' ')

    // Create area path (for gradient fill)
    const areaPath = `${path} L ${points[points.length - 1].x.toFixed(2)} ${height - padding} L ${padding} ${height - padding} Z`

    return {
      path,
      areaPath,
      points,
      min,
      max,
      lastValue: data[data.length - 1],
      firstValue: data[0]
    }
  }, [data, width, height])

  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center text-gray-600 text-xs"
        style={{ width, height }}
      >
        No data
      </div>
    )
  }

  const isPositive = lastValue >= firstValue
  const actualColor = color === 'auto'
    ? isPositive ? '#22c55e' : '#ef4444'
    : color

  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={`sparkline-gradient-${actualColor.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={actualColor} stopOpacity="0.3" />
          <stop offset="100%" stopColor={actualColor} stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Area fill */}
      {showArea && (
        <motion.path
          d={areaPath}
          fill={`url(#sparkline-gradient-${actualColor.replace('#', '')})`}
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ duration: 0.5 }}
        />
      )}

      {/* Line */}
      <motion.path
        d={path}
        fill="none"
        stroke={actualColor}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={animated ? { pathLength: 0, opacity: 0 } : undefined}
        animate={animated ? { pathLength: 1, opacity: 1 } : undefined}
        transition={{ duration: 1, ease: 'easeOut' }}
      />

      {/* Dots */}
      {showDots && points.map((point, i) => (
        <motion.circle
          key={i}
          cx={point.x}
          cy={point.y}
          r={2}
          fill={actualColor}
          initial={animated ? { scale: 0 } : undefined}
          animate={animated ? { scale: 1 } : undefined}
          transition={{ delay: 0.5 + i * 0.05 }}
        />
      ))}

      {/* Last point highlight */}
      <motion.circle
        cx={points[points.length - 1]?.x || 0}
        cy={points[points.length - 1]?.y || 0}
        r={3}
        fill={actualColor}
        initial={animated ? { scale: 0 } : undefined}
        animate={animated ? { scale: 1 } : undefined}
        transition={{ delay: 1 }}
      />
    </svg>
  )
}

// Stat box with integrated sparkline
interface SparklineStatProps {
  label: string
  value: string | number
  change?: number
  data: number[]
  prefix?: string
  suffix?: string
}

export function SparklineStat({
  label,
  value,
  change,
  data,
  prefix = '',
  suffix = ''
}: SparklineStatProps) {
  const isPositive = change !== undefined ? change >= 0 : true

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
      <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">
        {label}
      </div>

      <div className="flex items-end justify-between gap-4">
        <div>
          <div className="text-2xl font-black text-white tabular-nums">
            {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
          </div>
          {change !== undefined && (
            <div className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
              {isPositive ? '+' : ''}{change.toFixed(2)}%
            </div>
          )}
        </div>

        <Sparkline
          data={data}
          width={80}
          height={32}
          color="auto"
          showArea
        />
      </div>

      <div className="flex items-center justify-between mt-2 text-[10px] text-gray-600">
        <span>30d low: {prefix}{Math.min(...data).toFixed(2)}</span>
        <span>30d high: {prefix}{Math.max(...data).toFixed(2)}</span>
      </div>
    </div>
  )
}

// Generate mock historical data for demo
export function generateMockPriceData(currentPrice: number, days: number = 30, volatility: number = 0.02): number[] {
  const data: number[] = []
  let price = currentPrice * (1 - volatility * days / 2) // Start lower

  for (let i = 0; i < days; i++) {
    // Random walk with upward bias
    const change = (Math.random() - 0.45) * volatility * price
    price = Math.max(price + change, price * 0.95)
    data.push(Number(price.toFixed(2)))
  }

  // Ensure last value is close to current price
  data[data.length - 1] = currentPrice

  return data
}
