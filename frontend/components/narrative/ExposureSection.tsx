'use client'

import { motion } from 'framer-motion'
import { Building2, TrendingDown, Skull, BarChart3 } from 'lucide-react'
import { NarrativeSection } from './NarrativeSection'

interface BankExposure {
  name: string
  shortcut: string
  exposure: number
  estimatedLoss: number
  marketCap: number
  lossToMarketCap: number
  status: 'critical' | 'high' | 'elevated' | 'moderate'
}

interface ExposureSectionProps {
  banks: BankExposure[]
  totalExposure: number
  totalLoss: number
}

export function ExposureSection({
  banks = defaultBanks,
  totalExposure,
  totalLoss
}: ExposureSectionProps) {
  const status = banks.some(b => b.status === 'critical') ? 'critical' :
                 banks.some(b => b.status === 'high') ? 'warning' : 'active'

  const formatBillions = (num: number) => `$${(num / 1e9).toFixed(1)}B`

  return (
    <NarrativeSection
      id="exposure"
      phaseNumber={2}
      title="THE EXPOSURE"
      subtitle="Major banks hold massive silver short positions. As prices rise, potential losses compound rapidly, threatening solvency."
      status={status}
      flowText="Rising silver prices create losses on bank short positions"
    >
      {/* Total Exposure Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 text-center">
          <div className="text-sm text-gray-400 uppercase tracking-wider mb-2">Total Short Exposure</div>
          <div className="text-4xl font-black text-white">{formatBillions(totalExposure)}</div>
        </div>
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
          <div className="text-sm text-red-400 uppercase tracking-wider mb-2">Estimated Losses</div>
          <div className="text-4xl font-black text-red-400">{formatBillions(totalLoss)}</div>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6 text-center">
          <div className="text-sm text-amber-400 uppercase tracking-wider mb-2">Banks At Risk</div>
          <div className="text-4xl font-black text-amber-400">{banks.filter(b => b.status === 'critical' || b.status === 'high').length}</div>
        </div>
      </div>

      {/* Bank Cards - Domino Style */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <Skull className="w-4 h-4" />
          Bank Exposure Ranking
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {banks.map((bank, index) => (
            <motion.div
              key={bank.name}
              className={`relative overflow-hidden rounded-xl border ${
                bank.status === 'critical'
                  ? 'bg-red-500/10 border-red-500/30'
                  : bank.status === 'high'
                  ? 'bg-orange-500/10 border-orange-500/30'
                  : bank.status === 'elevated'
                  ? 'bg-amber-500/10 border-amber-500/30'
                  : 'bg-gray-900/50 border-gray-800'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {/* Status indicator bar */}
              <div
                className={`absolute left-0 top-0 bottom-0 w-1 ${
                  bank.status === 'critical'
                    ? 'bg-red-500'
                    : bank.status === 'high'
                    ? 'bg-orange-500'
                    : bank.status === 'elevated'
                    ? 'bg-amber-500'
                    : 'bg-gray-600'
                }`}
              />

              <div className="p-5 pl-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      bank.status === 'critical'
                        ? 'bg-red-500/20'
                        : bank.status === 'high'
                        ? 'bg-orange-500/20'
                        : 'bg-gray-800'
                    }`}>
                      <Building2 className={`w-5 h-5 ${
                        bank.status === 'critical'
                          ? 'text-red-400'
                          : bank.status === 'high'
                          ? 'text-orange-400'
                          : 'text-gray-400'
                      }`} />
                    </div>
                    <div>
                      <div className="font-bold text-white">{bank.name}</div>
                      <div className="text-xs text-gray-500">{bank.shortcut}</div>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    bank.status === 'critical'
                      ? 'bg-red-500/20 text-red-400'
                      : bank.status === 'high'
                      ? 'bg-orange-500/20 text-orange-400'
                      : bank.status === 'elevated'
                      ? 'bg-amber-500/20 text-amber-400'
                      : 'bg-gray-800 text-gray-400'
                  }`}>
                    {bank.status}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Exposure</div>
                    <div className="text-lg font-bold text-white">{formatBillions(bank.exposure)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Est. Loss</div>
                    <div className={`text-lg font-bold ${
                      bank.status === 'critical' ? 'text-red-400' : 'text-amber-400'
                    }`}>
                      {formatBillions(bank.estimatedLoss)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Loss/MCap</div>
                    <div className={`text-lg font-bold ${
                      bank.lossToMarketCap > 50 ? 'text-red-400' :
                      bank.lossToMarketCap > 25 ? 'text-orange-400' : 'text-amber-400'
                    }`}>
                      {bank.lossToMarketCap.toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Loss to Market Cap bar */}
                <div className="mt-4">
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        bank.lossToMarketCap > 50 ? 'bg-red-500' :
                        bank.lossToMarketCap > 25 ? 'bg-orange-500' : 'bg-amber-500'
                      }`}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(bank.lossToMarketCap, 100)}%` }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-600 mt-1">
                    <span>0%</span>
                    <span>Loss vs Market Cap</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Domino Effect Warning */}
      <motion.div
        className="mt-8 bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <TrendingDown className="w-5 h-5 text-red-400" />
          <h4 className="font-bold text-white">Domino Effect Risk</h4>
        </div>
        <p className="text-gray-400 text-sm">
          If one major bank faces a margin call or forced liquidation, it could trigger a cascade of selling
          across all short positions, accelerating price increases and amplifying losses for all exposed institutions.
        </p>
      </motion.div>
    </NarrativeSection>
  )
}

const defaultBanks: BankExposure[] = [
  {
    name: 'JPMorgan Chase',
    shortcut: 'JPM',
    exposure: 50000000000,
    estimatedLoss: 12400000000,
    marketCap: 450000000000,
    lossToMarketCap: 2.8,
    status: 'elevated'
  },
  {
    name: 'Citigroup',
    shortcut: 'C',
    exposure: 35000000000,
    estimatedLoss: 8700000000,
    marketCap: 95000000000,
    lossToMarketCap: 9.2,
    status: 'high'
  },
  {
    name: 'Bank of America',
    shortcut: 'BAC',
    exposure: 28000000000,
    estimatedLoss: 6900000000,
    marketCap: 230000000000,
    lossToMarketCap: 3.0,
    status: 'elevated'
  },
  {
    name: 'HSBC Holdings',
    shortcut: 'HSBC',
    exposure: 22000000000,
    estimatedLoss: 5400000000,
    marketCap: 150000000000,
    lossToMarketCap: 3.6,
    status: 'moderate'
  }
]
