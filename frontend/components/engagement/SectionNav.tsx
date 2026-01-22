'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Building2, Activity, Flame } from 'lucide-react'

interface Section {
  id: string
  label: string
  icon: React.ReactNode
  phase: number
}

const sections: Section[] = [
  { id: 'hero', label: 'Overview', icon: <Activity className="w-4 h-4" />, phase: 0 },
  { id: 'trigger', label: 'Trigger', icon: <Zap className="w-4 h-4" />, phase: 1 },
  { id: 'exposure', label: 'Exposure', icon: <Building2 className="w-4 h-4" />, phase: 2 },
  { id: 'cracks', label: 'Cracks', icon: <Activity className="w-4 h-4" />, phase: 3 },
  { id: 'cascade', label: 'Cascade', icon: <Flame className="w-4 h-4" />, phase: 4 },
]

export function SectionNav() {
  const [activeSection, setActiveSection] = useState('hero')
  const [isVisible, setIsVisible] = useState(false)

  // Track scroll position and active section
  useEffect(() => {
    const handleScroll = () => {
      // Show nav after scrolling past hero
      setIsVisible(window.scrollY > 400)

      // Determine active section
      const sectionElements = sections.map(s => ({
        id: s.id,
        element: document.getElementById(s.id)
      }))

      for (let i = sectionElements.length - 1; i >= 0; i--) {
        const section = sectionElements[i]
        if (section.element) {
          const rect = section.element.getBoundingClientRect()
          if (rect.top <= window.innerHeight / 2) {
            setActiveSection(section.id)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  if (!isVisible) return null

  return (
    <motion.nav
      className="fixed left-4 top-1/2 -translate-y-1/2 z-40 hidden lg:block"
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-2xl p-2 shadow-lg">
        <div className="flex flex-col gap-1">
          {sections.map((section) => {
            const isActive = activeSection === section.id

            return (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`group relative flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                  isActive
                    ? 'bg-red-500/20 text-red-400'
                    : 'text-gray-500 hover:text-white hover:bg-gray-800'
                }`}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-red-500 rounded-full"
                    layoutId="activeSection"
                  />
                )}

                {section.icon}

                {/* Label - expands on hover */}
                <span className={`text-sm font-medium whitespace-nowrap overflow-hidden transition-all ${
                  isActive ? 'w-16 opacity-100' : 'w-0 opacity-0 group-hover:w-16 group-hover:opacity-100'
                }`}>
                  {section.label}
                </span>

                {/* Phase number */}
                {section.phase > 0 && (
                  <span className={`absolute -right-1 -top-1 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center ${
                    isActive ? 'bg-red-500 text-white' : 'bg-gray-700 text-gray-400'
                  }`}>
                    {section.phase}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Progress indicator */}
        <div className="mt-2 px-3">
          <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-amber-500 to-red-500 rounded-full"
              initial={{ width: '0%' }}
              animate={{
                width: `${(sections.findIndex(s => s.id === activeSection) / (sections.length - 1)) * 100}%`
              }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </div>
    </motion.nav>
  )
}

// Mobile version - horizontal pills at top
export function MobileSectionNav() {
  const [activeSection, setActiveSection] = useState('hero')
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > 300)

      const sectionElements = sections.map(s => ({
        id: s.id,
        element: document.getElementById(s.id)
      }))

      for (let i = sectionElements.length - 1; i >= 0; i--) {
        const section = sectionElements[i]
        if (section.element) {
          const rect = section.element.getBoundingClientRect()
          if (rect.top <= window.innerHeight / 2) {
            setActiveSection(section.id)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  if (!isVisible) return null

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 lg:hidden bg-black/95 backdrop-blur-sm border-b border-gray-800"
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center gap-1 px-2 py-2 overflow-x-auto scrollbar-hide">
        {sections.slice(1).map((section) => {
          const isActive = activeSection === section.id

          return (
            <button
              key={section.id}
              onClick={() => scrollToSection(section.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'text-gray-500 border border-transparent'
              }`}
            >
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                isActive ? 'bg-red-500 text-white' : 'bg-gray-800'
              }`}>
                {section.phase}
              </span>
              {section.label}
            </button>
          )
        })}
      </div>
    </motion.nav>
  )
}
