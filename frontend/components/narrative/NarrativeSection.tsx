'use client'

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { ChevronRight, AlertTriangle, CheckCircle, Clock } from 'lucide-react'

interface NarrativeSectionProps {
  id: string
  phaseNumber: number
  title: string
  subtitle: string
  status: 'active' | 'warning' | 'critical' | 'complete'
  children: React.ReactNode
  flowText?: string
}

export function NarrativeSection({
  id,
  phaseNumber,
  title,
  subtitle,
  status,
  children,
  flowText
}: NarrativeSectionProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

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
          className="mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          {/* Phase indicator */}
          <div className="flex items-center gap-4 mb-4">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} ${config.border} border`}>
              <span className={`text-xs font-bold ${config.color}`}>PHASE {phaseNumber}</span>
            </div>
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${config.bg} ${config.border} border`}>
              {config.icon}
              <span className={`text-xs font-bold ${config.color}`}>{config.label}</span>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-4xl md:text-5xl font-black text-white mb-3 tracking-tight">
            {title}
          </h2>

          {/* Subtitle */}
          <p className="text-lg text-gray-400 max-w-2xl">
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

        {/* Section Content */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {children}
        </motion.div>
      </div>
    </section>
  )
}
