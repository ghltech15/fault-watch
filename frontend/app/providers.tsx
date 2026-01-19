'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { AuthProvider } from '@/lib/auth-context'
import { logVisit } from '@/lib/supabase'

function VisitorTracker() {
  useEffect(() => {
    const path = window.location.pathname
    const userAgent = navigator.userAgent
    const referrer = document.referrer || undefined
    logVisit(path, userAgent, referrer)
  }, [])

  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false)
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30000,
            refetchInterval: 60000,
            refetchOnWindowFocus: true,
          },
        },
      })
  )

  useEffect(() => {
    setMounted(true)
  }, [])

  // Don't render anything extra until client-side mount to prevent hydration issues
  if (!mounted) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <VisitorTracker />
        {children}
      </AuthProvider>
    </QueryClientProvider>
  )
}
