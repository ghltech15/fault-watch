'use client'

import { useState, useEffect } from 'react'
import { registerUser, verifyUser, submitComment, SocialMediaAccount } from '@/lib/api'

const SOCIAL_PLATFORMS = [
  { id: 'tiktok', name: 'TikTok', icon: '🎵', placeholder: '@username', color: 'from-pink-500 to-cyan-500' },
  { id: 'instagram', name: 'Instagram', icon: '📸', placeholder: '@username', color: 'from-purple-500 to-pink-500' },
  { id: 'youtube', name: 'YouTube', icon: '📺', placeholder: '@channel', color: 'from-red-500 to-red-600' },
  { id: 'twitter', name: 'X (Twitter)', icon: '𝕏', placeholder: '@handle', color: 'from-gray-600 to-gray-800' },
  { id: 'facebook', name: 'Facebook', icon: '📘', placeholder: 'username', color: 'from-blue-500 to-blue-700' },
  { id: 'reddit', name: 'Reddit', icon: '🤖', placeholder: 'u/username', color: 'from-orange-500 to-red-500' },
  { id: 'discord', name: 'Discord', icon: '💬', placeholder: 'username#0000', color: 'from-indigo-500 to-purple-600' },
  { id: 'telegram', name: 'Telegram', icon: '✈️', placeholder: '@username', color: 'from-blue-400 to-blue-600' },
] as const

type Platform = typeof SOCIAL_PLATFORMS[number]['id']

interface UserRegistrationProps {
  onRegistered: (userId: string) => void
  userId: string | null
}

interface AddedAccount {
  platform: Platform
  username: string
}

export function UserRegistrationCard({ onRegistered, userId }: UserRegistrationProps) {
  const [addedAccounts, setAddedAccounts] = useState<AddedAccount[]>([])
  const [currentPlatform, setCurrentPlatform] = useState<Platform>('tiktok')
  const [currentUsername, setCurrentUsername] = useState('')
  const [email, setEmail] = useState('')
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const addAccount = () => {
    if (!currentUsername.trim()) return

    // Check if platform already added
    if (addedAccounts.some(a => a.platform === currentPlatform)) {
      setError(`You've already added a ${SOCIAL_PLATFORMS.find(p => p.id === currentPlatform)?.name} account`)
      return
    }

    setAddedAccounts([...addedAccounts, { platform: currentPlatform, username: currentUsername.trim() }])
    setCurrentUsername('')
    setError('')

    // Auto-select next available platform
    const usedPlatforms = [...addedAccounts.map(a => a.platform), currentPlatform]
    const nextPlatform = SOCIAL_PLATFORMS.find(p => !usedPlatforms.includes(p.id))
    if (nextPlatform) {
      setCurrentPlatform(nextPlatform.id)
    }
  }

  const removeAccount = (platform: Platform) => {
    setAddedAccounts(addedAccounts.filter(a => a.platform !== platform))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Add current input if filled
    let finalAccounts = [...addedAccounts]
    if (currentUsername.trim() && !addedAccounts.some(a => a.platform === currentPlatform)) {
      finalAccounts.push({ platform: currentPlatform, username: currentUsername.trim() })
    }

    if (finalAccounts.length === 0) {
      setError('Please add at least one social media account')
      return
    }

    setIsSubmitting(true)

    try {
      const registration = {
        email: email || undefined,
        social_accounts: finalAccounts.map(a => ({ platform: a.platform, username: a.username })) as SocialMediaAccount[],
        primary_platform: finalAccounts[0].platform,
        comment: comment || undefined,
      }

      const result = await registerUser(registration)

      if (result.success) {
        localStorage.setItem('fault_watch_user_id', result.user_id)
        localStorage.setItem('fault_watch_accounts', JSON.stringify(finalAccounts))
        setSuccess(true)
        onRegistered(result.user_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (success || userId) {
    return (
      <div className="card bg-green-900/20 border-green-500/30">
        <div className="text-center py-4">
          <div className="text-4xl mb-2">✓</div>
          <h3 className="text-lg font-semibold text-green-400">Welcome to the Community!</h3>
          <p className="text-gray-400 text-sm mt-1">
            You have full access to all deep dive sections
          </p>
        </div>
      </div>
    )
  }

  const availablePlatforms = SOCIAL_PLATFORMS.filter(p => !addedAccounts.some(a => a.platform === p.id))

  return (
    <div className="card bg-gradient-to-br from-purple-900/20 to-blue-900/20 border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🌐</span>
        <h3 className="text-lg font-bold">Join the fault.watch Community</h3>
      </div>

      <p className="text-gray-400 text-sm mb-4">
        Connect all your social accounts so we can build a community across platforms.
        The more accounts you add, the easier it is for us to connect with you!
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Added Accounts Display */}
        {addedAccounts.length > 0 && (
          <div className="space-y-2">
            <label className="block text-sm text-gray-400">Your Connected Accounts</label>
            <div className="flex flex-wrap gap-2">
              {addedAccounts.map((account) => {
                const platform = SOCIAL_PLATFORMS.find(p => p.id === account.platform)!
                return (
                  <div
                    key={account.platform}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r ${platform.color} text-white text-sm`}
                  >
                    <span>{platform.icon}</span>
                    <span className="font-medium">{account.username}</span>
                    <button
                      type="button"
                      onClick={() => removeAccount(account.platform)}
                      className="ml-1 hover:bg-white/20 rounded-full w-5 h-5 flex items-center justify-center"
                    >
                      ×
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Platform Selection - Only show if platforms available */}
        {availablePlatforms.length > 0 && (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {addedAccounts.length > 0 ? 'Add Another Platform' : 'Select Your Platforms'}
              </label>
              <div className="grid grid-cols-4 gap-2">
                {availablePlatforms.map((platform) => (
                  <button
                    key={platform.id}
                    type="button"
                    onClick={() => setCurrentPlatform(platform.id)}
                    className={`p-2 rounded-lg text-center transition-all ${
                      currentPlatform === platform.id
                        ? 'bg-purple-600 border-purple-400 border-2 scale-105'
                        : 'bg-gray-800 border-gray-700 border hover:border-gray-500'
                    }`}
                  >
                    <div className="text-xl">{platform.icon}</div>
                    <div className="text-xs mt-1 truncate">{platform.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Username Input with Add Button */}
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Your {SOCIAL_PLATFORMS.find(p => p.id === currentPlatform)?.name} Username
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={currentUsername}
                  onChange={(e) => setCurrentUsername(e.target.value)}
                  placeholder={SOCIAL_PLATFORMS.find(p => p.id === currentPlatform)?.placeholder}
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addAccount()
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={addAccount}
                  disabled={!currentUsername.trim()}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    !currentUsername.trim()
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-500 text-white'
                  }`}
                >
                  + Add
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Press Enter or click Add, then select another platform
              </p>
            </div>
          </>
        )}

        {/* Email (Optional) */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Email <span className="text-gray-600">(for updates & alerts)</span>
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
          />
        </div>

        {/* Comment/Feedback */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            What would make fault.watch invaluable to you?
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Real-time alerts? More data sources? Mobile app? Tell us..."
            rows={3}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none resize-none"
          />
        </div>

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 px-3 py-2 rounded">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={(addedAccounts.length === 0 && !currentUsername.trim()) || isSubmitting}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            (addedAccounts.length === 0 && !currentUsername.trim()) || isSubmitting
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white'
          }`}
        >
          {isSubmitting ? 'Joining Community...' : `Join with ${addedAccounts.length + (currentUsername.trim() ? 1 : 0)} Account${addedAccounts.length + (currentUsername.trim() ? 1 : 0) !== 1 ? 's' : ''}`}
        </button>

        {addedAccounts.length >= 3 && (
          <div className="text-center text-sm text-green-400 animate-pulse">
            Power user detected! Thank you for connecting multiple platforms!
          </div>
        )}
      </form>

      <p className="text-xs text-gray-500 mt-3 text-center">
        Your socials help us build community across platforms. We never spam.
      </p>
    </div>
  )
}

// Persistent Feedback Card - Always visible to gather reactions and comments
export function FeedbackCard({ userId }: { userId: string | null }) {
  const [reaction, setReaction] = useState<string | null>(null)
  const [feedback, setFeedback] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const reactions = [
    { emoji: '🔥', label: 'Helpful', value: 'helpful' },
    { emoji: '🤯', label: 'Mind-blown', value: 'mindblown' },
    { emoji: '🤔', label: 'Confusing', value: 'confusing' },
    { emoji: '📈', label: 'Want More', value: 'want_more' },
    { emoji: '🐛', label: 'Found Bug', value: 'bug' },
    { emoji: '💡', label: 'Have Idea', value: 'idea' },
  ]

  const handleSubmit = async () => {
    if (!reaction && !feedback.trim()) return

    setIsSubmitting(true)
    try {
      await submitComment({
        user_id: userId || 'anonymous',
        comment: `[${reaction || 'feedback'}] ${feedback}`.trim(),
        page: 'dashboard',
      })
      setSubmitted(true)
      setReaction(null)
      setFeedback('')

      // Reset after 3 seconds
      setTimeout(() => setSubmitted(false), 3000)
    } catch (err) {
      console.error('Failed to submit feedback:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="card bg-gradient-to-br from-cyan-900/20 to-blue-900/20 border-cyan-500/30">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">💬</span>
        <h3 className="text-lg font-bold">Quick Feedback</h3>
      </div>

      {submitted ? (
        <div className="text-center py-4">
          <div className="text-4xl mb-2">🙏</div>
          <p className="text-green-400 font-semibold">Thanks for your feedback!</p>
          <p className="text-gray-400 text-sm">Your input shapes our roadmap</p>
        </div>
      ) : (
        <>
          <p className="text-gray-400 text-sm mb-3">
            How's fault.watch working for you? Your feedback directly influences what we build next.
          </p>

          {/* Quick Reactions */}
          <div className="flex flex-wrap gap-2 mb-3">
            {reactions.map((r) => (
              <button
                key={r.value}
                type="button"
                onClick={() => setReaction(reaction === r.value ? null : r.value)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm transition-all ${
                  reaction === r.value
                    ? 'bg-cyan-600 text-white scale-105'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span>{r.emoji}</span>
                <span>{r.label}</span>
              </button>
            ))}
          </div>

          {/* Comment Box */}
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Tell us more... What's working? What's not? What do you want?"
            rows={2}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-cyan-500 focus:outline-none resize-none text-sm mb-3"
          />

          <button
            onClick={handleSubmit}
            disabled={(!reaction && !feedback.trim()) || isSubmitting}
            className={`w-full py-2 rounded-lg font-semibold text-sm transition-all ${
              (!reaction && !feedback.trim()) || isSubmitting
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-cyan-600 hover:bg-cyan-500 text-white'
            }`}
          >
            {isSubmitting ? 'Sending...' : 'Send Feedback'}
          </button>
        </>
      )}
    </div>
  )
}

// Community Stats Card - Shows engagement
export function CommunityStatsCard() {
  const [stats, setStats] = useState<{ total_users: number; platforms: Record<string, number> } | null>(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://fault-watch-api.fly.dev'}/api/users/stats`)
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(() => {})
  }, [])

  if (!stats || stats.total_users < 5) return null

  return (
    <div className="card bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-green-500/30">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">👥</span>
        <h3 className="text-lg font-bold">Growing Community</h3>
      </div>
      <div className="text-center py-2">
        <div className="text-4xl font-black text-green-400">{stats.total_users}</div>
        <div className="text-gray-400 text-sm">Members watching the fault lines</div>
      </div>
      <div className="flex justify-center gap-2 mt-2">
        {Object.entries(stats.platforms || {}).slice(0, 5).map(([platform, count]) => {
          const p = SOCIAL_PLATFORMS.find(sp => sp.id === platform)
          if (!p || count < 1) return null
          return (
            <div key={platform} className="text-center">
              <div className="text-lg">{p.icon}</div>
              <div className="text-xs text-gray-500">{count}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Gate component that shows registration prompt if user isn't registered
export function AccessGate({
  children,
  userId,
  onRequestAccess
}: {
  children: React.ReactNode
  userId: string | null
  onRequestAccess: () => void
}) {
  if (userId) {
    return <>{children}</>
  }

  return (
    <div className="relative">
      <div className="blur-sm pointer-events-none opacity-50">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-xl">
        <div className="text-center p-6 max-w-sm">
          <div className="text-4xl mb-3">🔒</div>
          <h3 className="text-xl font-bold mb-2">Deep Dive Locked</h3>
          <p className="text-gray-400 text-sm mb-4">
            Join our community to unlock detailed analysis
          </p>
          <button
            onClick={onRequestAccess}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg font-semibold transition-all"
          >
            Join Community
          </button>
        </div>
      </div>
    </div>
  )
}

// Hook to manage user registration state
export function useUserAccess() {
  const [userId, setUserId] = useState<string | null>(null)
  const [isChecking, setIsChecking] = useState(true)
  const [showRegistration, setShowRegistration] = useState(false)

  useEffect(() => {
    const storedUserId = localStorage.getItem('fault_watch_user_id')
    if (storedUserId) {
      verifyUser(storedUserId)
        .then((result) => {
          if (result.valid && result.access_granted) {
            setUserId(storedUserId)
          } else {
            localStorage.removeItem('fault_watch_user_id')
          }
        })
        .catch(() => {
          setUserId(storedUserId)
        })
        .finally(() => setIsChecking(false))
    } else {
      setIsChecking(false)
    }
  }, [])

  const handleRegistered = (newUserId: string) => {
    setUserId(newUserId)
    setShowRegistration(false)
  }

  const requestAccess = () => {
    setShowRegistration(true)
  }

  return {
    userId,
    isChecking,
    showRegistration,
    setShowRegistration,
    handleRegistered,
    requestAccess,
    hasAccess: !!userId,
  }
}
