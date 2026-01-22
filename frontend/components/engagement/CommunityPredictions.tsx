'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, Clock, ChevronRight, Zap, Target } from 'lucide-react'

interface PredictionOption {
  id: string
  label: string
  votes: number
  color: string
}

export function CommunityPredictions() {
  const [hasVoted, setHasVoted] = useState(false)
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [totalVotes, setTotalVotes] = useState(4823)
  const [options, setOptions] = useState<PredictionOption[]>([
    { id: '30', label: 'Within 30 days', votes: 1687, color: '#ef4444' },
    { id: '60', label: '30-60 days', votes: 1446, color: '#f97316' },
    { id: '90', label: '60-90 days', votes: 1012, color: '#fbbf24' },
    { id: 'never', label: 'Not happening', votes: 678, color: '#64748b' },
  ])

  // Check if user has voted before (localStorage)
  useEffect(() => {
    const voted = localStorage.getItem('fw_prediction_voted')
    if (voted) {
      setHasVoted(true)
      setSelectedOption(voted)
    }
  }, [])

  const handleVote = (optionId: string) => {
    if (hasVoted) return

    // Update local state
    setOptions(prev =>
      prev.map(opt =>
        opt.id === optionId ? { ...opt, votes: opt.votes + 1 } : opt
      )
    )
    setTotalVotes(prev => prev + 1)
    setSelectedOption(optionId)
    setHasVoted(true)

    // Save to localStorage
    localStorage.setItem('fw_prediction_voted', optionId)
  }

  const getPercentage = (votes: number) => {
    return ((votes / totalVotes) * 100).toFixed(1)
  }

  const leadingOption = options.reduce((a, b) => (a.votes > b.votes ? a : b))

  return (
    <motion.div
      className="glass-card p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-500/20">
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-bold text-white">Community Prediction</h3>
            <p className="text-xs text-gray-400">When will silver hit $100?</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400">{totalVotes.toLocaleString()}</span>
          <span className="text-gray-600">votes</span>
        </div>
      </div>

      {/* Leading prediction highlight */}
      <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-cyan-500/10 border border-purple-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-gray-400">Leading prediction:</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-white">{leadingOption.label}</span>
            <span
              className="px-2 py-0.5 rounded text-xs font-bold"
              style={{ backgroundColor: `${leadingOption.color}33`, color: leadingOption.color }}
            >
              {getPercentage(leadingOption.votes)}%
            </span>
          </div>
        </div>
      </div>

      {/* Options */}
      <div className="space-y-3">
        {options.map((option, index) => {
          const percentage = parseFloat(getPercentage(option.votes))
          const isSelected = selectedOption === option.id
          const isLeading = option.id === leadingOption.id

          return (
            <motion.button
              key={option.id}
              onClick={() => handleVote(option.id)}
              disabled={hasVoted}
              className={`w-full relative overflow-hidden rounded-xl border transition-all ${
                hasVoted
                  ? isSelected
                    ? 'border-cyan-500/50'
                    : 'border-gray-700/50 opacity-80'
                  : 'border-gray-700 hover:border-purple-500/50 hover:bg-purple-500/5'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={!hasVoted ? { scale: 1.02 } : undefined}
              whileTap={!hasVoted ? { scale: 0.98 } : undefined}
            >
              {/* Progress bar background */}
              {hasVoted && (
                <motion.div
                  className="absolute inset-0 opacity-30"
                  style={{ backgroundColor: option.color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                />
              )}

              <div className="relative p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {isSelected && hasVoted && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-5 h-5 rounded-full bg-cyan-500 flex items-center justify-center"
                    >
                      <Zap className="w-3 h-3 text-white" />
                    </motion.div>
                  )}
                  <span className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                    {option.label}
                  </span>
                  {isLeading && hasVoted && (
                    <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs font-bold">
                      LEADING
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {hasVoted ? (
                    <>
                      <span className="text-sm text-gray-400">{option.votes.toLocaleString()}</span>
                      <span
                        className="text-lg font-bold"
                        style={{ color: option.color }}
                      >
                        {percentage}%
                      </span>
                    </>
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-500" />
                  )}
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* Vote prompt or thank you */}
      <div className="mt-6 text-center">
        {!hasVoted ? (
          <p className="text-sm text-gray-400">
            <Zap className="w-4 h-4 inline mr-1 text-purple-400" />
            Cast your vote to see community predictions
          </p>
        ) : (
          <motion.p
            className="text-sm text-cyan-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            Thanks for voting! Check back to see if you're right.
          </motion.p>
        )}
      </div>
    </motion.div>
  )
}

// Compact version for sidebar
export function CommunityPredictionsMini() {
  const leadingPercentage = 35
  const leadingLabel = 'Within 30 days'

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
      <div className="flex items-center gap-2">
        <Users className="w-4 h-4 text-purple-400" />
        <span className="text-sm text-gray-300">$100 prediction:</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-bold text-white">{leadingLabel}</span>
        <span className="text-sm font-bold text-purple-400">{leadingPercentage}%</span>
      </div>
    </div>
  )
}
