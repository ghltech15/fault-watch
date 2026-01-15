'use client'

import { useState, useEffect } from 'react'
import { registerUser, verifyUser, submitComment, SocialMediaAccount } from '@/lib/api'

const SOCIAL_PLATFORMS = [
  { id: 'tiktok', name: 'TikTok', icon: '🎵', placeholder: '@username' },
  { id: 'instagram', name: 'Instagram', icon: '📸', placeholder: '@username' },
  { id: 'youtube', name: 'YouTube', icon: '📺', placeholder: '@channel' },
  { id: 'twitter', name: 'X (Twitter)', icon: '𝕏', placeholder: '@handle' },
  { id: 'facebook', name: 'Facebook', icon: '📘', placeholder: 'username' },
] as const

type Platform = typeof SOCIAL_PLATFORMS[number]['id']

interface UserRegistrationProps {
  onRegistered: (userId: string) => void
  userId: string | null
}

export function UserRegistrationCard({ onRegistered, userId }: UserRegistrationProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('tiktok')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const registration = {
        email: email || undefined,
        social_accounts: [{ platform: selectedPlatform, username }] as SocialMediaAccount[],
        primary_platform: selectedPlatform,
        comment: comment || undefined,
      }

      const result = await registerUser(registration)

      if (result.success) {
        // Store in localStorage
        localStorage.setItem('fault_watch_user_id', result.user_id)
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
          <h3 className="text-lg font-semibold text-green-400">Access Granted!</h3>
          <p className="text-gray-400 text-sm mt-1">
            You now have full access to all deep dive sections
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card bg-gradient-to-br from-purple-900/20 to-blue-900/20 border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🔐</span>
        <h3 className="text-lg font-bold">Unlock Deep Dive Access</h3>
      </div>

      <p className="text-gray-400 text-sm mb-4">
        Enter your social media username to unlock detailed analysis, bank exposures,
        and crisis indicators. Help us build a better app!
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Platform Selection */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">Select Platform</label>
          <div className="grid grid-cols-5 gap-2">
            {SOCIAL_PLATFORMS.map((platform) => (
              <button
                key={platform.id}
                type="button"
                onClick={() => setSelectedPlatform(platform.id)}
                className={`p-2 rounded-lg text-center transition-all ${
                  selectedPlatform === platform.id
                    ? 'bg-purple-600 border-purple-400 border-2'
                    : 'bg-gray-800 border-gray-700 border hover:border-gray-500'
                }`}
              >
                <div className="text-xl">{platform.icon}</div>
                <div className="text-xs mt-1">{platform.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Username Input */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Your {SOCIAL_PLATFORMS.find(p => p.id === selectedPlatform)?.name} Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder={SOCIAL_PLATFORMS.find(p => p.id === selectedPlatform)?.placeholder}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
            required
          />
        </div>

        {/* Email (Optional) */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Email <span className="text-gray-600">(optional)</span>
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
            What features would you like to see?
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Tell us how we can make fault.watch better..."
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
          disabled={!username || isSubmitting}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            !username || isSubmitting
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-purple-600 hover:bg-purple-500 text-white'
          }`}
        >
          {isSubmitting ? 'Registering...' : 'Unlock Full Access'}
        </button>
      </form>

      <p className="text-xs text-gray-500 mt-3 text-center">
        We respect your privacy. Your info helps us understand our community.
      </p>
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
            Register with your social media to unlock detailed analysis
          </p>
          <button
            onClick={onRequestAccess}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg font-semibold transition-colors"
          >
            Unlock Access
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
    // Check localStorage for existing registration
    const storedUserId = localStorage.getItem('fault_watch_user_id')
    if (storedUserId) {
      // Verify with backend
      verifyUser(storedUserId)
        .then((result) => {
          if (result.valid && result.access_granted) {
            setUserId(storedUserId)
          } else {
            localStorage.removeItem('fault_watch_user_id')
          }
        })
        .catch(() => {
          // Keep local user if API fails
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
