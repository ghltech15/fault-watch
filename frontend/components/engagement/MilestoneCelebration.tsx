'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trophy, Share2, X, Sparkles, Star } from 'lucide-react'

interface MilestoneCelebrationProps {
  silverPrice: number
  onClose?: () => void
}

interface Milestone {
  price: number
  title: string
  subtitle: string
  color: string
  glowColor: string
}

const milestones: Milestone[] = [
  { price: 50, title: 'ALL-TIME HIGH BREACHED', subtitle: 'The 1980 record has fallen', color: '#22d3ee', glowColor: 'rgba(34, 211, 238, 0.6)' },
  { price: 75, title: 'CRITICAL THRESHOLD', subtitle: 'Major bank losses materializing', color: '#f59e0b', glowColor: 'rgba(245, 158, 11, 0.6)' },
  { price: 100, title: 'SYSTEMIC CRISIS', subtitle: 'Triple digits reached', color: '#ef4444', glowColor: 'rgba(239, 68, 68, 0.6)' },
  { price: 125, title: 'UNPRECEDENTED', subtitle: 'Uncharted territory', color: '#a855f7', glowColor: 'rgba(168, 85, 247, 0.6)' },
  { price: 150, title: 'COLLAPSE IMMINENT', subtitle: 'Point of no return', color: '#ef4444', glowColor: 'rgba(239, 68, 68, 0.8)' },
]

export function MilestoneCelebration({ silverPrice, onClose }: MilestoneCelebrationProps) {
  const [celebratingMilestone, setCelebratingMilestone] = useState<Milestone | null>(null)
  const [celebratedPrices, setCelebratedPrices] = useState<number[]>([])
  const [confetti, setConfetti] = useState<Array<{ id: number; x: number; color: string; delay: number }>>([])

  // Check for new milestones
  useEffect(() => {
    const reachedMilestone = milestones.find(
      m => silverPrice >= m.price && !celebratedPrices.includes(m.price)
    )

    if (reachedMilestone) {
      setCelebratingMilestone(reachedMilestone)
      setCelebratedPrices(prev => [...prev, reachedMilestone.price])

      // Generate confetti
      const newConfetti = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        color: ['#22d3ee', '#a855f7', '#ef4444', '#f59e0b', '#10b981'][Math.floor(Math.random() * 5)],
        delay: Math.random() * 0.5
      }))
      setConfetti(newConfetti)

      // Auto-close after 8 seconds
      const timer = setTimeout(() => {
        setCelebratingMilestone(null)
        setConfetti([])
      }, 8000)

      return () => clearTimeout(timer)
    }
  }, [silverPrice, celebratedPrices])

  const handleClose = useCallback(() => {
    setCelebratingMilestone(null)
    setConfetti([])
    onClose?.()
  }, [onClose])

  const handleShare = useCallback(() => {
    if (!celebratingMilestone) return

    const text = `SILVER JUST HIT $${celebratingMilestone.price}! ${celebratingMilestone.title} - I was watching live on fault.watch`
    const url = 'https://fault.watch'

    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
      '_blank'
    )
  }, [celebratingMilestone])

  return (
    <AnimatePresence>
      {celebratingMilestone && (
        <motion.div
          className="fixed inset-0 z-[200] flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0"
            style={{
              background: `radial-gradient(circle at center, ${celebratingMilestone.glowColor} 0%, rgba(15, 23, 42, 0.95) 70%)`,
            }}
            onClick={handleClose}
          />

          {/* Confetti */}
          {confetti.map(piece => (
            <motion.div
              key={piece.id}
              className="absolute w-3 h-3 rounded-sm"
              style={{
                left: `${piece.x}%`,
                backgroundColor: piece.color,
                boxShadow: `0 0 10px ${piece.color}`,
              }}
              initial={{ top: -20, rotate: 0, opacity: 1 }}
              animate={{
                top: '110%',
                rotate: 720,
                opacity: 0,
              }}
              transition={{
                duration: 3,
                delay: piece.delay,
                ease: 'linear',
              }}
            />
          ))}

          {/* Content */}
          <motion.div
            className="relative z-10 text-center px-8"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ type: 'spring', damping: 15 }}
          >
            {/* Close button */}
            <button
              onClick={handleClose}
              className="absolute -top-4 -right-4 p-2 bg-gray-800 rounded-full hover:bg-gray-700 transition"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Trophy icon */}
            <motion.div
              className="mb-6"
              animate={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
            >
              <Trophy
                className="w-20 h-20 mx-auto"
                style={{ color: celebratingMilestone.color }}
              />
            </motion.div>

            {/* Sparkles */}
            <motion.div
              className="absolute -top-10 left-1/2 -translate-x-1/2"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <Sparkles className="w-8 h-8 text-yellow-400" />
            </motion.div>

            {/* Price */}
            <motion.div
              className="text-8xl md:text-9xl font-black mb-4"
              style={{
                color: celebratingMilestone.color,
                textShadow: `0 0 40px ${celebratingMilestone.glowColor}, 0 0 80px ${celebratingMilestone.glowColor}`,
              }}
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              ${celebratingMilestone.price}
            </motion.div>

            {/* Title */}
            <h2 className="text-3xl md:text-4xl font-black text-white mb-2">
              {celebratingMilestone.title}
            </h2>

            {/* Subtitle */}
            <p className="text-xl text-gray-300 mb-8">
              {celebratingMilestone.subtitle}
            </p>

            {/* Badge */}
            <motion.div
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full mb-8"
              style={{
                background: `linear-gradient(135deg, ${celebratingMilestone.color}33 0%, rgba(15, 23, 42, 0.8) 100%)`,
                border: `2px solid ${celebratingMilestone.color}`,
              }}
              animate={{ boxShadow: [`0 0 20px ${celebratingMilestone.glowColor}`, `0 0 40px ${celebratingMilestone.glowColor}`, `0 0 20px ${celebratingMilestone.glowColor}`] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <Star className="w-5 h-5" style={{ color: celebratingMilestone.color }} />
              <span className="text-white font-bold">YOU WERE HERE</span>
              <Star className="w-5 h-5" style={{ color: celebratingMilestone.color }} />
            </motion.div>

            {/* Share button */}
            <div>
              <button
                onClick={handleShare}
                className="flex items-center gap-3 mx-auto px-8 py-4 bg-blue-500 hover:bg-blue-600 rounded-xl text-white font-bold transition transform hover:scale-105"
              >
                <Share2 className="w-5 h-5" />
                Share This Moment
              </button>
            </div>

            {/* Timestamp */}
            <p className="text-gray-500 text-sm mt-6">
              {new Date().toLocaleString()} • fault.watch
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Demo trigger for testing
export function MilestoneDemo() {
  const [demoPrice, setDemoPrice] = useState(95)

  return (
    <div className="fixed bottom-24 right-4 z-50 bg-gray-800 rounded-lg p-4">
      <p className="text-xs text-gray-400 mb-2">Demo: Trigger Milestone</p>
      <div className="flex gap-2">
        {[100, 125, 150].map(price => (
          <button
            key={price}
            onClick={() => setDemoPrice(price)}
            className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded text-sm hover:bg-purple-500/30"
          >
            ${price}
          </button>
        ))}
      </div>
      <MilestoneCelebration silverPrice={demoPrice} />
    </div>
  )
}
