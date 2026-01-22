'use client'

import { motion, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState } from 'react'
import { ChevronRight, ChevronDown, AlertTriangle, CheckCircle, Clock, Minimize2, Maximize2 } from 'lucide-react'

interface NarrativeSectionProps {
  id: string
  phaseNumber: number
  title: string
  subtitle: string
  status: 'active' | 'warning' | 'critical' | 'complete'
  children: React.ReactNode
  flowText?: string
  defaultExpanded?: boolean
  collapsible?: boolean
}

export function NarrativeSection({
  id,
  phaseNumber,
  title,
  subtitle,
  status,
  children,
  flowText,
  defaultExpanded = true,
  collapsible = true
}: NarrativeSectionProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const statusConfig = {
    active: {
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      icon: <Clock className="w-4 h-4" />,
      label: 'MONITORING'
    },
    warning: {
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      icon: <AlertTriangle className="w-4 h-4" />,
      label: 'WARNING'
    },
    critical: {
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      icon: <AlertTriangle className="w-4 h-4" />,
      label: 'CRITICAL'
    },
    complete: {
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      icon: <CheckCircle className="w-4 h-4" />,
      label: 'COMPLETE'
    }
  }

  const config = statusConfig[status]

  return (
    <section
      id={id}
      ref={ref}
      className="relative py-16 md:py-24"
    >
      {/* Flow connector (shows relationship to previous section) */}
      {flowText && (
        <motion.div
          className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 bg-gray-900 px-4 py-2 rounded-full border border-gray-800"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <ChevronRight className="w-4 h-4 text-gray-500" />
          <span className="text-xs text-gray-400">{flowText}</span>
        </motion.div>
      )}

      <div className="max-w-6xl mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className={`${collapsible ? 'cursor-pointer' : ''} ${isExpanded ? 'mb-12' : 'mb-4'}`}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          onClick={collapsible ? () => setIsExpanded(!isExpanded) : undefined}
        >
          {/* Phase indicator and collapse button row */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} ${config.border} border`}>
                <span className={`text-xs font-bold ${config.color}`}>PHASE {phaseNumber}</span>
              </div>
              <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${config.bg} ${config.border} border`}>
                {config.icon}
                <span className={`text-xs font-bold ${config.color}`}>{config.label}</span>
              </div>
            </div>

            {/* Collapse/Expand button */}
            {collapsible && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsExpanded(!isExpanded)
                }}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 transition text-gray-400 hover:text-white"
              >
                {isExpanded ? (
                  <>
                    <Minimize2 className="w-4 h-4" />
                    <span className="text-xs font-medium hidden sm:inline">Collapse</span>
                  </>
                ) : (
                  <>
                    <Maximize2 className="w-4 h-4" />
                    <span className="text-xs font-medium hidden sm:inline">Expand</span>
                  </>
                )}
              </button>
            )}
          </div>

          {/* Title */}
          <div className="flex items-center gap-3">
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight">
              {title}
            </h2>
            {collapsible && (
              <ChevronDown
                className={`w-8 h-8 text-gray-500 transition-transform duration-300 ${
                  isExpanded ? 'rotate-180' : ''
                }`}
              />
            )}
          </div>

          {/* Subtitle - always visible as preview */}
          <p className={`text-lg text-gray-400 max-w-2xl mt-3 ${!isExpanded ? 'line-clamp-2' : ''}`}>
            {subtitle}
          </p>

          {/* Decorative line */}
          <div className={`mt-6 h-1 w-24 rounded-full ${config.bg}`} style={{
            background: `linear-gradient(90deg, ${
              status === 'critical' ? 'rgb(239,68,68)' :
              status === 'warning' ? 'rgb(245,158,11)' :
              status === 'active' ? 'rgb(59,130,246)' : 'rgb(52,211,153)'
            }, transparent)`
          }} />
        </motion.div>

        {/* Section Content - Collapsible */}
        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {children}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Collapsed preview hint */}
        {!isExpanded && collapsible && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-4"
          >
            <span className="text-xs text-gray-500">
              Click to expand section
            </span>
          </motion.div>
        )}
      </div>
    </section>
  )
}
