'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { HeroSection } from '@/components/hero'
import {
  TriggerSection,
  ExposureSection,
  CracksSection,
  CascadeSection
} from '@/components/narrative'
import { CreatorToolbar } from '@/components/creator'
import {
  LiveIndicators,
  SectionNav,
  MobileSectionNav,
  ProjectionCard,
  MilestoneCelebration,
  CommunityPredictions,
  CommunityContributionModal,
  CommunityStatsWidget,
  NewsSummary
} from '@/components/engagement'
import { useState, useEffect, useRef } from 'react'

export default function Home() {
  const [currentSection, setCurrentSection] = useState('hero')
  const initialSilverPriceRef = useRef<number | null>(null)

  // Fetch dashboard data
  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
    refetchInterval: 300000, // 5 minutes
  })

  // Fetch crisis gauge data
  const { data: crisisGauge } = useQuery({
    queryKey: ['crisisGauge'],
    queryFn: api.getCrisisGauge,
    refetchInterval: 300000,
  })

  // Fetch cascade data
  const { data: cascade } = useQuery({
    queryKey: ['cascade'],
    queryFn: api.getCascade,
    refetchInterval: 300000,
  })

  // Track current section for screenshots
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setCurrentSection(entry.target.id || 'hero')
          }
        })
      },
      { threshold: 0.5 }
    )

    const sections = document.querySelectorAll('[data-section]')
    sections.forEach((section) => observer.observe(section))

    return () => observer.disconnect()
  }, [])

  // Calculate derived data for sections
  const silverPrice = dashboard?.prices?.silver?.price || 95.02
  const silverChange = dashboard?.prices?.silver?.change_pct || 0
  const comexInventory = 280.5 // Million oz (would come from API)

  // Capture initial silver price on first load
  useEffect(() => {
    if (silverPrice && initialSilverPriceRef.current === null) {
      initialSilverPriceRef.current = silverPrice
    }
  }, [silverPrice])

  // Bank exposure data (derived from crisis gauge losses or defaults)
  const getLossForBank = (bankName: string, defaultLoss: number) => {
    const bankLoss = crisisGauge?.losses?.find(l =>
      l.entity.toLowerCase().includes(bankName.toLowerCase())
    )
    return bankLoss?.total_loss || defaultLoss
  }

  const banks = [
    {
      name: 'JPMorgan Chase',
      shortcut: 'JPM',
      exposure: 50000000000,
      estimatedLoss: getLossForBank('JPMorgan', 12400000000),
      marketCap: 450000000000,
      lossToMarketCap: 2.8,
      status: 'elevated' as const
    },
    {
      name: 'Citigroup',
      shortcut: 'C',
      exposure: 35000000000,
      estimatedLoss: 8700000000,
      marketCap: 95000000000,
      lossToMarketCap: 9.2,
      status: 'high' as const
    },
    {
      name: 'Bank of America',
      shortcut: 'BAC',
      exposure: 28000000000,
      estimatedLoss: 6900000000,
      marketCap: 230000000000,
      lossToMarketCap: 3.0,
      status: 'elevated' as const
    },
    {
      name: 'HSBC Holdings',
      shortcut: 'HSBC',
      exposure: 22000000000,
      estimatedLoss: 5400000000,
      marketCap: 150000000000,
      lossToMarketCap: 3.6,
      status: 'moderate' as const
    }
  ]

  const totalExposure = banks.reduce((sum, b) => sum + b.exposure, 0)
  const totalLoss = banks.reduce((sum, b) => sum + b.estimatedLoss, 0)

  // Crack indicators (derived from crisis gauge or defaults)
  const crackIndicators = [
    { name: 'Credit Default Swaps', category: 'tier1' as const, status: 'stressed' as const, description: 'Bank CDS spreads widening', currentValue: '+45 bps', threshold: '+100 bps' },
    { name: 'Repo Market Stress', category: 'tier1' as const, status: 'stable' as const, description: 'Overnight funding rates', currentValue: '5.35%', threshold: '6.0%' },
    { name: 'COMEX Delivery Failures', category: 'tier1' as const, status: 'stressed' as const, description: 'Physical delivery backlog', currentValue: '12 days', threshold: '30 days' },
    { name: 'Bank Stock Volatility', category: 'tier1' as const, status: 'stable' as const, description: 'Financial sector VIX', currentValue: '24.5', threshold: '40' },
    { name: 'Gold-Silver Ratio', category: 'tier2' as const, status: 'stressed' as const, description: 'Abnormal ratio movement', currentValue: '78:1', threshold: '100:1' },
    { name: 'LBMA Forward Rates', category: 'tier2' as const, status: 'stable' as const, description: 'London forward curve', currentValue: 'Normal', threshold: 'Inverted' },
    { name: 'ETF Outflows', category: 'tier2' as const, status: 'stable' as const, description: 'SLV/PSLV redemptions', currentValue: '-2.3M oz', threshold: '-10M oz' },
    { name: 'Dealer Positioning', category: 'tier2' as const, status: 'stressed' as const, description: 'COT report shorts', currentValue: '142K', threshold: '200K' },
    { name: 'Fed Facility Usage', category: 'tier3' as const, status: 'stable' as const, description: 'Emergency lending', currentValue: '$0.2B', threshold: '$50B' },
    { name: 'Treasury Volatility', category: 'tier3' as const, status: 'stable' as const, description: 'MOVE index', currentValue: '98', threshold: '150' },
    { name: 'Dollar Liquidity', category: 'tier3' as const, status: 'stable' as const, description: 'Global USD shortage', currentValue: 'Normal', threshold: 'Stressed' },
    { name: 'Interbank Lending', category: 'tier3' as const, status: 'stable' as const, description: 'LIBOR-OIS spread', currentValue: '12 bps', threshold: '50 bps' }
  ]

  const cracksActive = crackIndicators.filter(i => i.status !== 'stable').length
  const totalCracks = crackIndicators.length

  // Cascade phase - use crisis gauge current_phase if available, otherwise cascade stage
  const currentPhase = crisisGauge?.current_phase || cascade?.stage || 2
  // Intervention risk derived from crisis probability
  const interventionRisk = crisisGauge?.crisis_probability
    ? Math.min(Math.round(crisisGauge.crisis_probability * 0.5), 100)
    : 35

  return (
    <main id="main-content" className="min-h-screen">
      {/* Milestone Celebration Overlay */}
      <MilestoneCelebration silverPrice={silverPrice} />

      {/* Community Contribution Modal */}
      <CommunityContributionModal />

      {/* Live Engagement Indicators */}
      <LiveIndicators
        initialSilverPrice={initialSilverPriceRef.current || silverPrice}
        currentSilverPrice={silverPrice}
      />

      {/* Section Navigation */}
      <SectionNav />
      <MobileSectionNav />

      {/* Hero Section */}
      <div data-section id="hero">
        {dashboard && <HeroSection dashboard={dashboard} />}
      </div>

      {/* Latest Analysis / News Summary */}
      <NewsSummary />

      {/* Narrative Timeline */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        {/* Section 1: The Trigger */}
        <div data-section id="trigger">
          <TriggerSection
            silverPrice={silverPrice}
            silverChange={silverChange}
            comexInventory={comexInventory}
          />

          {/* Price Projections Card */}
          <div className="max-w-6xl mx-auto px-4 -mt-8 mb-8">
            <ProjectionCard
              currentPrice={silverPrice}
              dailyChangePercent={Math.abs(silverChange) || 0.5}
            />
          </div>
        </div>

        {/* Section 2: The Exposure */}
        <div data-section id="exposure">
          <ExposureSection
            banks={banks}
            totalExposure={totalExposure}
            totalLoss={totalLoss}
          />
        </div>

        {/* Section 3: The Cracks */}
        <div data-section id="cracks">
          <CracksSection
            indicators={crackIndicators}
            cracksActive={cracksActive}
            totalCracks={totalCracks}
          />
        </div>

        {/* Section 4: The Cascade */}
        <div data-section id="cascade">
          <CascadeSection
            currentPhase={currentPhase}
            interventionRisk={interventionRisk}
          />
        </div>

        {/* Community Section */}
        <div className="max-w-2xl mx-auto mt-16 space-y-6">
          {/* Global Watch Party Stats */}
          <CommunityStatsWidget />

          {/* Community Predictions */}
          <CommunityPredictions />
        </div>
      </div>

      {/* Creator Toolbar */}
      <CreatorToolbar currentSection={currentSection} />
    </main>
  )
}
