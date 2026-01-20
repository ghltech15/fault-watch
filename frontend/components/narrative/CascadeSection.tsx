'use client'

import { motion } from 'framer-motion'
import { Flame, Shield, Clock, ChevronRight, AlertTriangle, CheckCircle } from 'lucide-react'
import { NarrativeSection } from './NarrativeSection'

interface CascadePhase {
  phase: number
  name: string
  description: string
  triggers: string[]
  status: 'complete' | 'active' | 'pending'
}

interface CascadeSectionProps {
  currentPhase: number
  phases?: CascadePhase[]
  interventionRisk: number
}

export function CascadeSection({
  currentPhase,
  phases = defaultPhases,
  interventionRisk
}: CascadeSectionProps) {
  const status = currentPhase >= 4 ? 'critical' : currentPhase >= 3 ? 'warning' : 'active'

  return (
    <NarrativeSection
      id="cascade"
      phaseNumber={4}
      title="THE CASCADE"
      subtitle="The progression from isolated stress to systemic crisis. Each phase triggers the next in an accelerating feedback loop."
      status={status}
      flowText="Systemic stress spreads, creating cascade failure risk"
    >
      {/* Current Phase Highlight */}
      <div className="bg-gradient-to-r from-red-500/10 via-orange-500/10 to-amber-500/10 border border-red-500/30 rounded-2xl p-8 mb-8">
        <div className="text-center">
          <div className="text-sm text-gray-400 uppercase tracking-wider mb-2">Current Cascade Phase</div>
          <div className="text-8xl font-black text-white mb-2">{currentPhase}</div>
          <div className={`text-2xl font-bold ${
            currentPhase >= 4 ? 'text-red-400' :
            currentPhase >= 3 ? 'text-orange-400' :
            currentPhase >= 2 ? 'text-amber-400' : 'text-green-400'
          }`}>
            {phases[currentPhase - 1]?.name || 'UNKNOWN'}
          </div>
          <p className="text-gray-400 text-sm mt-2 max-w-xl mx-auto">
            {phases[currentPhase - 1]?.description}
          </p>
        </div>
      </div>

      {/* Phase Timeline */}
      <div className="relative mb-8">
        {/* Progress line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-800" />
        <motion.div
          className="absolute left-8 top-0 w-0.5 bg-gradient-to-b from-red-500 to-amber-500"
          initial={{ height: 0 }}
          animate={{ height: `${((currentPhase - 1) / (phases.length - 1)) * 100}%` }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />

        <div className="space-y-6">
          {phases.map((phase, index) => {
            const isActive = phase.phase === currentPhase
            const isComplete = phase.phase < currentPhase

            return (
              <motion.div
                key={phase.phase}
                className="relative flex gap-6"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {/* Phase indicator */}
                <div className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center font-black text-2xl ${
                  isComplete
                    ? 'bg-green-500/20 border-2 border-green-500 text-green-400'
                    : isActive
                    ? 'bg-amber-500/20 border-2 border-amber-500 text-amber-400 animate-pulse'
                    : 'bg-gray-800 border-2 border-gray-700 text-gray-500'
                }`}>
                  {isComplete ? <CheckCircle className="w-8 h-8" /> : phase.phase}
                </div>

                {/* Phase content */}
                <div className={`flex-1 pb-6 ${index < phases.length - 1 ? 'border-b border-gray-800' : ''}`}>
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className={`text-xl font-bold ${
                      isComplete ? 'text-green-400' :
                      isActive ? 'text-amber-400' : 'text-gray-400'
                    }`}>
                      {phase.name}
                    </h4>
                    {isActive && (
                      <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs font-bold rounded animate-pulse">
                        CURRENT
                      </span>
                    )}
                    {isComplete && (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded">
                        PASSED
                      </span>
                    )}
                  </div>

                  <p className="text-gray-400 text-sm mb-3">{phase.description}</p>

                  {/* Triggers */}
                  <div className="space-y-1">
                    {phase.triggers.map((trigger, i) => (
                      <div
                        key={i}
                        className={`flex items-center gap-2 text-xs ${
                          isComplete ? 'text-green-400/70' :
                          isActive ? 'text-amber-400/70' : 'text-gray-600'
                        }`}
                      >
                        <ChevronRight className="w-3 h-3" />
                        {trigger}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Government Intervention Risk */}
      <motion.div
        className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-500/20 rounded-lg">
            <Shield className="w-6 h-6 text-purple-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-bold text-white">Government Intervention Probability</h4>
              <span className={`text-2xl font-black ${
                interventionRisk > 70 ? 'text-red-400' :
                interventionRisk > 40 ? 'text-amber-400' : 'text-green-400'
              }`}>
                {interventionRisk}%
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              When systemic risk reaches critical levels, government intervention becomes likely.
              This could include trading halts, forced position liquidations, or bailouts.
            </p>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${
                  interventionRisk > 70 ? 'bg-red-500' :
                  interventionRisk > 40 ? 'bg-amber-500' : 'bg-green-500'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${interventionRisk}%` }}
                transition={{ duration: 1.5 }}
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* What to Watch */}
      <div className="mt-8 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          What to Watch For
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            'Sudden bank stock drops > 10%',
            'COMEX delivery backlog > 30 days',
            'Credit default swap spikes',
            'Fed emergency facility activation',
            'Trading halts on precious metals',
            'Bank dividend suspensions'
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-gray-400">
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              {item}
            </div>
          ))}
        </div>
      </div>
    </NarrativeSection>
  )
}

const defaultPhases: CascadePhase[] = [
  {
    phase: 1,
    name: 'STABLE',
    description: 'Markets functioning normally. Silver positions manageable. No stress signals.',
    triggers: ['Normal trading volumes', 'Stable credit spreads', 'Adequate COMEX inventory'],
    status: 'complete'
  },
  {
    phase: 2,
    name: 'ELEVATED',
    description: 'Credit spreads widening. Silver delivery pressure building. Early stress indicators.',
    triggers: ['CDS spreads +20-50bps', 'COMEX inventory declining', 'Increased hedging activity'],
    status: 'active'
  },
  {
    phase: 3,
    name: 'STRESSED',
    description: 'Bank losses materializing. COMEX inventory critical. Credit markets tightening.',
    triggers: ['CDS spreads +50-100bps', 'Delivery delays > 7 days', 'Bank stock volatility > 30%'],
    status: 'pending'
  },
  {
    phase: 4,
    name: 'CRITICAL',
    description: 'Bank insolvency imminent. Margin calls cascading. Flight to safety accelerating.',
    triggers: ['CDS spreads +100-200bps', 'COMEX delivery failures', 'Interbank lending freeze'],
    status: 'pending'
  },
  {
    phase: 5,
    name: 'SYSTEMIC',
    description: 'Multiple bank failures. Credit frozen. Fed emergency intervention likely.',
    triggers: ['Bank failures announced', 'Trading halts', 'Government intervention activated'],
    status: 'pending'
  }
]
