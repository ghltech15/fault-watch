'use client'

import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'

interface CrisisGaugeProps {
  percentage: number
  phase: number
  cracksShowing: number
  totalCracks: number
  size?: 'large' | 'medium' | 'small'
}

export function CrisisGauge({
  percentage,
  phase,
  cracksShowing,
  totalCracks,
  size = 'large'
}: CrisisGaugeProps) {
  const [displayPercentage, setDisplayPercentage] = useState(0)
  const [isAnimating, setIsAnimating] = useState(true)

  // Animate the percentage on mount
  useEffect(() => {
    setIsAnimating(true)
    const duration = 2000 // 2 seconds
    const startTime = Date.now()
    const startValue = displayPercentage

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = startValue + (percentage - startValue) * eased

      setDisplayPercentage(Math.round(current))

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setIsAnimating(false)
      }
    }

    requestAnimationFrame(animate)
  }, [percentage])

  const getColor = () => {
    if (percentage >= 80) return '#dc2626' // Critical red
    if (percentage >= 60) return '#ea580c' // High orange
    if (percentage >= 40) return '#f59e0b' // Elevated amber
    if (percentage >= 20) return '#eab308' // Moderate yellow
    return '#22c55e' // Low green
  }

  const getLabel = () => {
    if (percentage >= 80) return 'CRITICAL'
    if (percentage >= 60) return 'HIGH'
    if (percentage >= 40) return 'ELEVATED'
    if (percentage >= 20) return 'MODERATE'
    return 'LOW'
  }

  const color = getColor()
  const label = getLabel()

  // SVG dimensions based on size
  const dimensions = {
    large: { size: 320, stroke: 16, fontSize: 72 },
    medium: { size: 200, stroke: 12, fontSize: 48 },
    small: { size: 120, stroke: 8, fontSize: 28 }
  }

  const { size: svgSize, stroke, fontSize } = dimensions[size]
  const radius = (svgSize - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * 0.75 // 270 degrees
  const offset = arcLength * (1 - displayPercentage / 100)

  return (
    <div className="relative flex flex-col items-center">
      {/* Glow effect */}
      <div
        className="absolute rounded-full blur-3xl opacity-30"
        style={{
          width: svgSize * 1.2,
          height: svgSize * 1.2,
          backgroundColor: color,
          animation: percentage >= 60 ? 'pulse 2s ease-in-out infinite' : 'none'
        }}
      />

      {/* SVG Gauge */}
      <svg
        width={svgSize}
        height={svgSize}
        viewBox={`0 0 ${svgSize} ${svgSize}`}
        className="relative z-10 transform -rotate-[135deg]"
      >
        {/* Background arc */}
        <circle
          cx={svgSize / 2}
          cy={svgSize / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${circumference}`}
        />

        {/* Progress arc */}
        <motion.circle
          cx={svgSize / 2}
          cy={svgSize / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={offset}
          initial={{ strokeDashoffset: arcLength }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            filter: `drop-shadow(0 0 ${stroke}px ${color})`
          }}
        />
      </svg>

      {/* Center content */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center"
        style={{ paddingTop: size === 'large' ? '20px' : '10px' }}
      >
        <motion.span
          className="font-black tabular-nums"
          style={{
            fontSize: fontSize,
            color: color,
            textShadow: `0 0 30px ${color}, 0 0 60px ${color}`,
            lineHeight: 1
          }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          {displayPercentage}%
        </motion.span>

        <motion.span
          className="text-xs font-bold tracking-[0.3em] mt-2 uppercase"
          style={{ color: color }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          {label}
        </motion.span>

        {size === 'large' && (
          <motion.span
            className="text-gray-500 text-xs mt-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
          >
            CRISIS PROBABILITY
          </motion.span>
        )}
      </div>

      {/* Phase and cracks indicators (large only) */}
      {size === 'large' && (
        <div className="flex items-center gap-6 mt-6">
          <div className="text-center">
            <div className="text-3xl font-black text-white">{phase}</div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">Phase</div>
          </div>
          <div className="w-px h-10 bg-gray-700" />
          <div className="text-center">
            <div className="text-3xl font-black text-amber-400">{cracksShowing}/{totalCracks}</div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">Cracks</div>
          </div>
        </div>
      )}
    </div>
  )
}
