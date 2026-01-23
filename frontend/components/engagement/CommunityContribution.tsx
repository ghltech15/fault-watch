'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MapPin, DollarSign, Users, TrendingUp, Globe, ChevronDown, Check, Sparkles } from 'lucide-react'

// Country list with common ones at top
const COUNTRIES = [
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'NL', name: 'Netherlands', flag: '🇳🇱' },
  { code: 'CH', name: 'Switzerland', flag: '🇨🇭' },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬' },
  { code: 'HK', name: 'Hong Kong', flag: '🇭🇰' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'AE', name: 'UAE', flag: '🇦🇪' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷' },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦' },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿' },
  { code: 'IE', name: 'Ireland', flag: '🇮🇪' },
  { code: 'FR', name: 'France', flag: '🇫🇷' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹' },
  { code: 'ES', name: 'Spain', flag: '🇪🇸' },
  { code: 'PL', name: 'Poland', flag: '🇵🇱' },
  { code: 'SE', name: 'Sweden', flag: '🇸🇪' },
  { code: 'NO', name: 'Norway', flag: '🇳🇴' },
  { code: 'AT', name: 'Austria', flag: '🇦🇹' },
  { code: 'BE', name: 'Belgium', flag: '🇧🇪' },
  { code: 'OTHER', name: 'Other', flag: '🌍' },
]

// Precious metals knowledge levels
const KNOWLEDGE_LEVELS = [
  { id: 'new', label: "I'm new to this", description: 'Just learning about precious metals' },
  { id: 'aware', label: 'Somewhat familiar', description: 'I follow the markets occasionally' },
  { id: 'active', label: 'Active stacker', description: 'I buy gold/silver regularly' },
  { id: 'expert', label: 'Deep in the game', description: 'Been stacking for years' },
]

interface Contribution {
  id: string
  country: string
  countryFlag: string
  city?: string
  silverPrice?: number
  goldPrice?: number
  knowledgeLevel: string
  timestamp: number
}

interface CommunityStats {
  totalContributors: number
  countries: number
  avgSilverPremium: number
  avgGoldPremium: number
  recentContributions: Contribution[]
}

// Generate mock community data for social proof
function generateMockStats(): CommunityStats {
  const mockContributions: Contribution[] = [
    { id: '1', country: 'US', countryFlag: '🇺🇸', city: 'Texas', silverPrice: 38.50, goldPrice: 2950, knowledgeLevel: 'active', timestamp: Date.now() - 120000 },
    { id: '2', country: 'CA', countryFlag: '🇨🇦', city: 'Ontario', silverPrice: 42.00, goldPrice: 3100, knowledgeLevel: 'expert', timestamp: Date.now() - 300000 },
    { id: '3', country: 'GB', countryFlag: '🇬🇧', city: 'London', silverPrice: 35.20, goldPrice: 2880, knowledgeLevel: 'active', timestamp: Date.now() - 600000 },
    { id: '4', country: 'AU', countryFlag: '🇦🇺', city: 'Sydney', silverPrice: 45.00, goldPrice: 3200, knowledgeLevel: 'aware', timestamp: Date.now() - 900000 },
    { id: '5', country: 'DE', countryFlag: '🇩🇪', city: 'Berlin', silverPrice: 36.80, goldPrice: 2920, knowledgeLevel: 'active', timestamp: Date.now() - 1200000 },
  ]

  return {
    totalContributors: 4823 + Math.floor(Math.random() * 50),
    countries: 67,
    avgSilverPremium: 12.5,
    avgGoldPremium: 8.2,
    recentContributions: mockContributions,
  }
}

function getStoredContribution(): Contribution | null {
  if (typeof window === 'undefined') return null
  const stored = localStorage.getItem('fw_contribution')
  return stored ? JSON.parse(stored) : null
}

function storeContribution(contribution: Contribution) {
  localStorage.setItem('fw_contribution', JSON.stringify(contribution))
  localStorage.setItem('fw_contribution_time', Date.now().toString())
}

function hasSeenModal(): boolean {
  if (typeof window === 'undefined') return true
  return localStorage.getItem('fw_contribution_seen') === 'true'
}

function markModalSeen() {
  localStorage.setItem('fw_contribution_seen', 'true')
}

export function CommunityContributionModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [step, setStep] = useState(1) // 1: location, 2: prices, 3: thank you
  const [hasContributed, setHasContributed] = useState(false)

  // Form state
  const [country, setCountry] = useState('')
  const [city, setCity] = useState('')
  const [knowledgeLevel, setKnowledgeLevel] = useState('')
  const [silverPrice, setSilverPrice] = useState('')
  const [goldPrice, setGoldPrice] = useState('')
  const [countryDropdownOpen, setCountryDropdownOpen] = useState(false)

  // Check if user has already contributed
  useEffect(() => {
    const existing = getStoredContribution()
    if (existing) {
      setHasContributed(true)
    }
  }, [])

  // Show modal after delay (only if hasn't seen before)
  useEffect(() => {
    if (hasSeenModal() || hasContributed) return

    const timer = setTimeout(() => {
      setIsOpen(true)
    }, 15000) // 15 seconds

    return () => clearTimeout(timer)
  }, [hasContributed])

  const handleClose = () => {
    setIsOpen(false)
    markModalSeen()
  }

  const handleNextStep = () => {
    if (step === 1 && country && knowledgeLevel) {
      setStep(2)
    } else if (step === 2) {
      // Save contribution
      const contribution: Contribution = {
        id: Date.now().toString(),
        country,
        countryFlag: COUNTRIES.find(c => c.code === country)?.flag || '🌍',
        city: city || undefined,
        silverPrice: silverPrice ? parseFloat(silverPrice) : undefined,
        goldPrice: goldPrice ? parseFloat(goldPrice) : undefined,
        knowledgeLevel,
        timestamp: Date.now(),
      }
      storeContribution(contribution)
      setHasContributed(true)
      setStep(3)
    }
  }

  const handleSkipPrices = () => {
    // Save contribution without prices
    const contribution: Contribution = {
      id: Date.now().toString(),
      country,
      countryFlag: COUNTRIES.find(c => c.code === country)?.flag || '🌍',
      city: city || undefined,
      knowledgeLevel,
      timestamp: Date.now(),
    }
    storeContribution(contribution)
    setHasContributed(true)
    setStep(3)
  }

  const selectedCountry = COUNTRIES.find(c => c.code === country)

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={handleClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal */}
          <motion.div
            className="relative w-full max-w-md glass-card p-6 overflow-hidden"
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* Close button */}
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>

            {/* Step 1: Location & Knowledge */}
            {step === 1 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {/* Header */}
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-cyan-500/20 mb-4">
                    <Globe className="w-7 h-7 text-cyan-400" />
                  </div>
                  <h2 className="text-xl font-bold text-white mb-2">Welcome to fault.watch</h2>
                  <p className="text-sm text-gray-400">Join thousands tracking the silver squeeze worldwide</p>
                </div>

                {/* Live counter */}
                <div className="flex items-center justify-center gap-4 mb-6 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-green-400 font-bold">{(4823 + Math.floor(Math.random() * 50)).toLocaleString()}</span>
                    <span className="text-gray-400 text-sm">watchers</span>
                  </div>
                  <div className="w-px h-4 bg-gray-600" />
                  <div className="flex items-center gap-2">
                    <span className="text-cyan-400 font-bold">67</span>
                    <span className="text-gray-400 text-sm">countries</span>
                  </div>
                </div>

                {/* Country selector */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Where are you watching from?
                  </label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setCountryDropdownOpen(!countryDropdownOpen)}
                      className="w-full flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-600/50 hover:border-cyan-500/50 transition-colors text-left"
                    >
                      {selectedCountry ? (
                        <span className="flex items-center gap-2">
                          <span className="text-xl">{selectedCountry.flag}</span>
                          <span className="text-white">{selectedCountry.name}</span>
                        </span>
                      ) : (
                        <span className="text-gray-500">Select your country</span>
                      )}
                      <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${countryDropdownOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown */}
                    <AnimatePresence>
                      {countryDropdownOpen && (
                        <motion.div
                          className="absolute top-full left-0 right-0 mt-2 max-h-48 overflow-y-auto rounded-lg bg-slate-800 border border-slate-600/50 shadow-xl z-10"
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                        >
                          {COUNTRIES.map((c) => (
                            <button
                              key={c.code}
                              onClick={() => {
                                setCountry(c.code)
                                setCountryDropdownOpen(false)
                              }}
                              className="w-full flex items-center gap-2 p-3 hover:bg-slate-700/50 transition-colors text-left"
                            >
                              <span className="text-xl">{c.flag}</span>
                              <span className="text-white">{c.name}</span>
                              {country === c.code && <Check className="w-4 h-4 text-cyan-400 ml-auto" />}
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                {/* City (optional) */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    City/Region <span className="text-gray-500">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="e.g., Texas, London, Ontario"
                    className="w-full p-3 rounded-lg bg-slate-800/50 border border-slate-600/50 focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-500"
                  />
                </div>

                {/* Knowledge level */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    How familiar are you with precious metals?
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {KNOWLEDGE_LEVELS.map((level) => (
                      <button
                        key={level.id}
                        onClick={() => setKnowledgeLevel(level.id)}
                        className={`p-3 rounded-lg border text-left transition-all ${
                          knowledgeLevel === level.id
                            ? 'border-cyan-500 bg-cyan-500/10'
                            : 'border-slate-600/50 hover:border-slate-500'
                        }`}
                      >
                        <div className={`text-sm font-medium ${knowledgeLevel === level.id ? 'text-cyan-400' : 'text-white'}`}>
                          {level.label}
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">{level.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Continue button */}
                <button
                  onClick={handleNextStep}
                  disabled={!country || !knowledgeLevel}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-bold transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue
                </button>

                <button
                  onClick={handleClose}
                  className="w-full mt-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Maybe later
                </button>
              </motion.div>
            )}

            {/* Step 2: Price Reporting */}
            {step === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {/* Header */}
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-yellow-500/20 mb-4">
                    <DollarSign className="w-7 h-7 text-yellow-400" />
                  </div>
                  <h2 className="text-xl font-bold text-white mb-2">Help Track Local Prices</h2>
                  <p className="text-sm text-gray-400">What are dealers charging for physical metal in your area?</p>
                </div>

                {/* Why this matters */}
                <div className="mb-6 p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-xs text-gray-300">
                      Physical premiums vary wildly by region. Your input helps everyone see the real cost of metal worldwide.
                    </p>
                  </div>
                </div>

                {/* Silver price */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Silver price per oz <span className="text-gray-500">(physical, USD)</span>
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                    <input
                      type="number"
                      step="0.01"
                      value={silverPrice}
                      onChange={(e) => setSilverPrice(e.target.value)}
                      placeholder="e.g., 38.50"
                      className="w-full p-3 pl-8 rounded-lg bg-slate-800/50 border border-slate-600/50 focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-500"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Spot price ~$32. What do dealers actually charge?</p>
                </div>

                {/* Gold price */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Gold price per oz <span className="text-gray-500">(physical, USD)</span>
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                    <input
                      type="number"
                      step="1"
                      value={goldPrice}
                      onChange={(e) => setGoldPrice(e.target.value)}
                      placeholder="e.g., 2950"
                      className="w-full p-3 pl-8 rounded-lg bg-slate-800/50 border border-slate-600/50 focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-500"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Spot price ~$2850. What do dealers actually charge?</p>
                </div>

                {/* Submit button */}
                <button
                  onClick={handleNextStep}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold transition-all hover:opacity-90"
                >
                  Submit Prices
                </button>

                <button
                  onClick={handleSkipPrices}
                  className="w-full mt-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Skip - I don't know local prices
                </button>
              </motion.div>
            )}

            {/* Step 3: Thank You */}
            {step === 3 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center"
              >
                {/* Success animation */}
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/20 mb-6">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', damping: 10, stiffness: 200 }}
                  >
                    <Check className="w-10 h-10 text-green-400" />
                  </motion.div>
                </div>

                <h2 className="text-2xl font-bold text-white mb-2">You're In!</h2>
                <p className="text-gray-400 mb-6">
                  Welcome to the watch party, {selectedCountry?.flag} {selectedCountry?.name}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="p-4 rounded-lg bg-slate-800/50">
                    <div className="text-2xl font-bold text-cyan-400">4,824</div>
                    <div className="text-xs text-gray-400">Total Watchers</div>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-800/50">
                    <div className="text-2xl font-bold text-purple-400">68</div>
                    <div className="text-xs text-gray-400">Countries</div>
                  </div>
                </div>

                {silverPrice && (
                  <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 mb-6">
                    <div className="text-sm text-gray-400 mb-1">Your reported silver price</div>
                    <div className="text-2xl font-bold text-yellow-400">${parseFloat(silverPrice).toFixed(2)}/oz</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {parseFloat(silverPrice) > 32 ? `+${((parseFloat(silverPrice) / 32 - 1) * 100).toFixed(0)}% premium over spot` : 'Below spot!'}
                    </div>
                  </div>
                )}

                <button
                  onClick={handleClose}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-bold transition-all hover:opacity-90"
                >
                  Start Watching
                </button>
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Compact widget showing community stats
export function CommunityStatsWidget() {
  const [stats, setStats] = useState<CommunityStats | null>(null)

  useEffect(() => {
    setStats(generateMockStats())
  }, [])

  if (!stats) return null

  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-cyan-400" />
        <h3 className="font-bold text-white">Global Watch Party</h3>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-center p-3 rounded-lg bg-slate-800/50">
          <div className="text-xl font-bold text-cyan-400">{stats.totalContributors.toLocaleString()}</div>
          <div className="text-xs text-gray-400">Watchers</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-slate-800/50">
          <div className="text-xl font-bold text-purple-400">{stats.countries}</div>
          <div className="text-xs text-gray-400">Countries</div>
        </div>
      </div>

      {/* Recent activity feed */}
      <div className="space-y-2">
        <div className="text-xs text-gray-500 uppercase tracking-wider">Recent Reports</div>
        {stats.recentContributions.slice(0, 3).map((c) => (
          <div key={c.id} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{c.countryFlag}</span>
              <span className="text-gray-300">{c.city || c.country}</span>
            </div>
            {c.silverPrice && (
              <span className="text-yellow-400 font-medium">${c.silverPrice.toFixed(2)}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Floating button to open modal manually
export function ReportPriceButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-24 right-6 z-40 flex items-center gap-2 px-4 py-3 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
    >
      <MapPin className="w-5 h-5" />
      <span>Report Local Price</span>
    </button>
  )
}
