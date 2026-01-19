'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { supabase, VisitorLog, UserProfile } from '@/lib/supabase'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users,
  Eye,
  TrendingUp,
  Clock,
  Globe,
  LogOut,
  Mail,
  Lock,
  AlertCircle,
  BarChart3,
  UserCheck,
  Activity,
  MousePointer,
  Calendar,
  RefreshCw,
  Shield,
  Zap
} from 'lucide-react'

export default function AdminPage() {
  const { user, loading, signIn, signOut, isAdmin } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [visitors, setVisitors] = useState<VisitorLog[]>([])
  const [users, setUsers] = useState<UserProfile[]>([])
  const [activeTab, setActiveTab] = useState<'analytics' | 'users'>('analytics')
  const [statsLoading, setStatsLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (user && isAdmin) {
      fetchData()
    }
  }, [user, isAdmin])

  async function fetchData() {
    setStatsLoading(true)

    const { data: visitorData } = await supabase
      .from('visitor_logs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(500)

    if (visitorData) setVisitors(visitorData)

    const { data: userData } = await supabase
      .from('user_profiles')
      .select('*')
      .order('created_at', { ascending: false })

    if (userData) setUsers(userData)

    setStatsLoading(false)
  }

  async function handleRefresh() {
    setRefreshing(true)
    await fetchData()
    setTimeout(() => setRefreshing(false), 500)
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    const { error } = await signIn(email, password)
    if (error) setError(error.message)
  }

  // Calculate analytics
  const todayVisits = visitors.filter(v => {
    const visitDate = new Date(v.created_at).toDateString()
    return visitDate === new Date().toDateString()
  }).length

  const weekVisits = visitors.filter(v => {
    const visitDate = new Date(v.created_at)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return visitDate >= weekAgo
  }).length

  const monthVisits = visitors.filter(v => {
    const visitDate = new Date(v.created_at)
    const monthAgo = new Date()
    monthAgo.setDate(monthAgo.getDate() - 30)
    return visitDate >= monthAgo
  }).length

  const uniqueVisitors = new Set(visitors.map(v => v.user_agent)).size

  const topPages = visitors.reduce((acc, v) => {
    acc[v.path] = (acc[v.path] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const sortedPages = Object.entries(topPages)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  // Get visits by hour for today
  const hourlyData = Array(24).fill(0)
  visitors.forEach(v => {
    const date = new Date(v.created_at)
    if (date.toDateString() === new Date().toDateString()) {
      hourlyData[date.getHours()]++
    }
  })
  const maxHourly = Math.max(...hourlyData, 1)

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <RefreshCw className="w-8 h-8 text-emerald-400" />
        </motion.div>
      </div>
    )
  }

  // Login form
  if (!user) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4 relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md relative z-10"
        >
          <div className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
                className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/20"
              >
                <Shield className="w-8 h-8 text-white" />
              </motion.div>
              <h1 className="text-2xl font-bold text-white mb-2">Admin Portal</h1>
              <p className="text-gray-500 text-sm">fault.watch dashboard</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wider">Email</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#0a0a0f] border border-gray-800 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
                    placeholder="admin@example.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wider">Password</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#0a0a0f] border border-gray-800 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 p-3 rounded-xl"
                  >
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.button
                type="submit"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg shadow-emerald-500/20"
              >
                Sign In
              </motion.button>
            </form>
          </div>
        </motion.div>
      </div>
    )
  }

  // Access denied for non-admins
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-red-500/20 rounded-2xl p-8 text-center max-w-md"
        >
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
          <h1 className="text-xl font-bold text-white mb-2">Access Denied</h1>
          <p className="text-gray-400 mb-6">You don't have admin privileges.</p>
          <button
            onClick={signOut}
            className="text-gray-400 hover:text-white transition-colors text-sm"
          >
            Sign out and try another account
          </button>
        </motion.div>
      </div>
    )
  }

  // Admin dashboard
  return (
    <div className="min-h-screen bg-[#0a0a0f] relative">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4"
          >
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
              </div>
              <p className="text-gray-500 text-sm ml-13">fault.watch analytics & user management</p>
            </div>
            <div className="flex items-center gap-3">
              <motion.button
                onClick={handleRefresh}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 px-4 py-2 bg-[#16161f] border border-gray-800 rounded-xl text-gray-400 hover:text-white hover:border-gray-700 transition-all"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </motion.button>
              <div className="flex items-center gap-3 px-4 py-2 bg-[#16161f] border border-gray-800 rounded-xl">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                <span className="text-gray-400 text-sm">{user.email}</span>
              </div>
              <motion.button
                onClick={signOut}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 px-4 py-2 bg-[#16161f] border border-gray-800 rounded-xl text-gray-400 hover:text-red-400 hover:border-red-500/30 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
            </div>
          </motion.div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Today', value: todayVisits, icon: Eye, color: 'emerald', sublabel: 'page views' },
              { label: 'This Week', value: weekVisits, icon: TrendingUp, color: 'blue', sublabel: 'page views' },
              { label: 'Unique Visitors', value: uniqueVisitors, icon: Users, color: 'purple', sublabel: 'all time' },
              { label: 'Registered', value: users.length, icon: UserCheck, color: 'amber', sublabel: 'users' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="group relative bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-5 overflow-hidden hover:border-gray-700/50 transition-all"
              >
                <div className={`absolute inset-0 bg-gradient-to-br from-${stat.color}-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity`} />
                <div className="relative">
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2.5 bg-${stat.color}-500/10 rounded-xl`}>
                      <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                    </div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider">{stat.label}</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">{stat.value.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">{stat.sublabel}</div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Hourly Activity Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-6 mb-8"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/10 rounded-xl">
                  <Activity className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Today's Activity</h3>
                  <p className="text-xs text-gray-500">Hourly page views</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Calendar className="w-4 h-4" />
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
              </div>
            </div>
            <div className="flex items-end gap-1 h-32">
              {hourlyData.map((count, hour) => (
                <motion.div
                  key={hour}
                  initial={{ height: 0 }}
                  animate={{ height: `${(count / maxHourly) * 100}%` }}
                  transition={{ delay: 0.5 + hour * 0.02, duration: 0.5 }}
                  className="flex-1 relative group"
                >
                  <div
                    className={`absolute bottom-0 w-full rounded-t-sm transition-colors ${
                      hour === new Date().getHours()
                        ? 'bg-gradient-to-t from-emerald-500 to-emerald-400'
                        : 'bg-gradient-to-t from-gray-700 to-gray-600 group-hover:from-blue-500 group-hover:to-blue-400'
                    }`}
                    style={{ height: `${Math.max((count / maxHourly) * 100, 2)}%` }}
                  />
                  <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-gray-600">
                    {hour % 6 === 0 ? `${hour}:00` : ''}
                  </div>
                  {count > 0 && (
                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                      {count}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            {[
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              { id: 'users', label: 'Users', icon: Users },
            ].map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl transition-all ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-emerald-500/20 to-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-[#16161f] text-gray-400 border border-gray-800 hover:border-gray-700 hover:text-white'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </motion.button>
            ))}
          </div>

          {/* Content */}
          <AnimatePresence mode="wait">
            {activeTab === 'analytics' && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="grid lg:grid-cols-2 gap-6"
              >
                {/* Top Pages */}
                <div className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-purple-500/10 rounded-xl">
                      <MousePointer className="w-5 h-5 text-purple-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">Top Pages</h3>
                  </div>
                  {sortedPages.length > 0 ? (
                    <div className="space-y-3">
                      {sortedPages.map(([path, count], i) => {
                        const percentage = (count / visitors.length) * 100
                        return (
                          <motion.div
                            key={path}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="relative"
                          >
                            <div className="flex items-center justify-between relative z-10 py-2">
                              <div className="flex items-center gap-3">
                                <span className="w-6 h-6 bg-gray-800 rounded-lg flex items-center justify-center text-xs text-gray-400">
                                  {i + 1}
                                </span>
                                <span className="text-white font-medium">{path || '/'}</span>
                              </div>
                              <span className="text-gray-400 text-sm">{count} views</span>
                            </div>
                            <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-purple-500/20 to-transparent rounded-full" style={{ width: `${percentage}%` }} />
                          </motion.div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Globe className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No page view data yet</p>
                    </div>
                  )}
                </div>

                {/* Recent Visits */}
                <div className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-emerald-500/10 rounded-xl">
                      <Clock className="w-5 h-5 text-emerald-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">Recent Visits</h3>
                  </div>
                  {visitors.length > 0 ? (
                    <div className="space-y-2 max-h-80 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
                      {visitors.slice(0, 20).map((visit, i) => (
                        <motion.div
                          key={visit.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: i * 0.05 }}
                          className="flex items-center justify-between py-2 px-3 rounded-xl hover:bg-gray-800/30 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                            <span className="text-white text-sm">{visit.path || '/'}</span>
                          </div>
                          <span className="text-gray-500 text-xs">
                            {new Date(visit.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No visits recorded yet</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {activeTab === 'users' && (
              <motion.div
                key="users"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-gradient-to-b from-[#16161f] to-[#0f0f15] border border-gray-800/50 rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-amber-500/10 rounded-xl">
                    <Users className="w-5 h-5 text-amber-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">Registered Users</h3>
                  <span className="ml-auto px-3 py-1 bg-gray-800 rounded-full text-xs text-gray-400">
                    {users.length} total
                  </span>
                </div>
                {users.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
                          <th className="pb-4 font-medium">User</th>
                          <th className="pb-4 font-medium">Role</th>
                          <th className="pb-4 font-medium">Joined</th>
                          <th className="pb-4 font-medium">Last Active</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((u, i) => (
                          <motion.tr
                            key={u.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: i * 0.05 }}
                            className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors"
                          >
                            <td className="py-4">
                              <div className="flex items-center gap-3">
                                <div className="w-9 h-9 bg-gradient-to-br from-gray-700 to-gray-800 rounded-xl flex items-center justify-center text-white font-medium text-sm">
                                  {u.email.charAt(0).toUpperCase()}
                                </div>
                                <span className="text-white">{u.email}</span>
                              </div>
                            </td>
                            <td className="py-4">
                              <span className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                                u.role === 'admin'
                                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                  : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                              }`}>
                                {u.role}
                              </span>
                            </td>
                            <td className="py-4 text-gray-400 text-sm">
                              {new Date(u.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-4 text-gray-400 text-sm">
                              {u.last_sign_in ? new Date(u.last_sign_in).toLocaleString() : 'Never'}
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Users className="w-10 h-10 mx-auto mb-3 opacity-50" />
                    <p>No users registered yet</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
