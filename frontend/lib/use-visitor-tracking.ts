'use client'

import { useEffect } from 'react'
import { logVisit } from './supabase'

export function useVisitorTracking() {
  useEffect(() => {
    // Only track on client side
    if (typeof window === 'undefined') return

    const path = window.location.pathname
    const userAgent = navigator.userAgent
    const referrer = document.referrer || undefined

    // Log the visit
    logVisit(path, userAgent, referrer)
  }, [])
}
