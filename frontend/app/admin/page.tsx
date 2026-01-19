'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { supabase, VisitorLog, UserProfile } from '@/lib/supabase'
import { motion } from 'framer-motion'
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
  ChevronRight,
  BarChart3,
  UserCheck
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

  useEffect(() => {
    if (user && isAdmin) {
      fetchData()
    }
  }, [user, isAdmin])

  async function fetchData() {
    setStatsLoading(true)

    // Fetch visitor logs
    const { data: visitorData } = await supabase
      .from('visitor_logs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(500)

    if (visitorData) setVisitors(visitorData)

    // Fetch users
    const { data: userData } = await supabase
      .from('user_profiles')
      .select('*')
      .order('created_at', { ascending: false })

    if (userData) setUsers(userData)

    setStatsLoading(false)
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    const { error } = await signIn(email, password)
    if (error) {
      setError(error.message)
    }
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

  const uniqueVisitors = new Set(visitors.map(v => v.user_agent)).size

  const topPages = visitors.reduce((acc, v) => {
    acc[v.path] = (acc[v.path] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const sortedPages = Object.entries(topPages)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-400"></div>
      </div>
    )
  }

  // Login form
  if (!user) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="bg-[#12121a] border border-gray-800 rounded-xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-white mb-2">Admin Login</h1>
              <p className="text-gray-400 text-sm">fault.watch dashboard</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#0a0a0f] border border-gray-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                    placeholder="admin@example.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#0a0a0f] border border-gray-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                    placeholder="********"
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 p-3 rounded-lg">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-medium py-3 rounded-lg transition-colors"
              >
                Sign In
              </button>
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
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-8 text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-white mb-2">Access Denied</h1>
          <p className="text-gray-400 mb-6">You don't have admin privileges.</p>
          <button
            onClick={signOut}
            className="text-gray-400 hover:text-white transition-colors"
          >
            Sign out and try another account
          </button>
        </div>
      </div>
    )
  }

  // Admin dashboard
  return (
    <div className="min-h-screen bg-[#0a0a0f] p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-gray-400 text-sm">fault.watch analytics & user management</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm">{user.email}</span>
            <button
              onClick={signOut}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[#12121a] border border-gray-800 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <Eye className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-gray-400 text-sm">Today</span>
            </div>
            <div className="text-2xl font-bold text-white">{todayVisits}</div>
            <div className="text-xs text-gray-500">page views</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-[#12121a] border border-gray-800 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-gray-400 text-sm">This Week</span>
            </div>
            <div className="text-2xl font-bold text-white">{weekVisits}</div>
            <div className="text-xs text-gray-500">page views</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-[#12121a] border border-gray-800 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Users className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-gray-400 text-sm">Unique Visitors</span>
            </div>
            <div className="text-2xl font-bold text-white">{uniqueVisitors}</div>
            <div className="text-xs text-gray-500">all time</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-[#12121a] border border-gray-800 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-amber-500/10 rounded-lg">
                <UserCheck className="w-5 h-5 text-amber-400" />
              </div>
              <span className="text-gray-400 text-sm">Registered</span>
            </div>
            <div className="text-2xl font-bold text-white">{users.length}</div>
            <div className="text-xs text-gray-500">users</div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'analytics'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-[#12121a] text-gray-400 border border-gray-800 hover:border-gray-700'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'users'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-[#12121a] text-gray-400 border border-gray-800 hover:border-gray-700'
            }`}
          >
            <Users className="w-4 h-4" />
            Users
          </button>
        </div>

        {/* Content */}
        {activeTab === 'analytics' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Top Pages */}
            <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Top Pages</h3>
              {sortedPages.length > 0 ? (
                <div className="space-y-3">
                  {sortedPages.map(([path, count], i) => (
                    <div key={path} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-gray-500 text-sm w-4">{i + 1}</span>
                        <span className="text-white">{path || '/'}</span>
                      </div>
                      <span className="text-gray-400">{count} views</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No page view data yet</p>
              )}
            </div>

            {/* Recent Visits */}
            <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Visits</h3>
              {visitors.length > 0 ? (
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {visitors.slice(0, 20).map((visit) => (
                    <div key={visit.id} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-gray-500" />
                        <span className="text-white">{visit.path || '/'}</span>
                      </div>
                      <span className="text-gray-500">
                        {new Date(visit.created_at).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No visits recorded yet</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Registered Users</h3>
            {users.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 text-sm border-b border-gray-800">
                      <th className="pb-3">Email</th>
                      <th className="pb-3">Role</th>
                      <th className="pb-3">Joined</th>
                      <th className="pb-3">Last Sign In</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-b border-gray-800/50">
                        <td className="py-3 text-white">{u.email}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            u.role === 'admin'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="py-3 text-gray-400">
                          {new Date(u.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 text-gray-400">
                          {u.last_sign_in ? new Date(u.last_sign_in).toLocaleString() : 'Never'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">No users registered yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
