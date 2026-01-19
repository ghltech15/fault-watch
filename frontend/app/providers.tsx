'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { AuthProvider } from '@/lib/auth-context'
import { logVisit } from '@/lib/supabase'

function VisitorTracker() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    const path = window.location.pathname
    const userAgent = navigator.userAgent
    const referrer = document.referrer || undefined

    logVisit(path, userAgent, referrer)
  }, [mounted])

  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
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

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <VisitorTracker />
        {children}
      </AuthProvider>
    </QueryClientProvider>
  )
}
