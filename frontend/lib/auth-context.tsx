'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { getSupabase } from './supabase'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>
  signOut: () => Promise<void>
  isAdmin: boolean
}

const defaultContext: AuthContextType = {
  user: null,
  session: null,
  loading: true,
  signIn: async () => ({ error: null }),
  signUp: async () => ({ error: null }),
  signOut: async () => {},
  isAdmin: false
}

const AuthContext = createContext<AuthContextType>(defaultContext)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAdmin, setIsAdmin] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    const supabase = getSupabase()

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      checkAdminStatus(session?.user?.id)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        checkAdminStatus(session?.user?.id)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [mounted])

  async function checkAdminStatus(userId: string | undefined) {
    if (!userId) {
      setIsAdmin(false)
      return
    }

    const supabase = getSupabase()
    const { data } = await supabase
      .from('user_profiles')
      .select('role')
      .eq('id', userId)
      .single()

    setIsAdmin(data?.role === 'admin')
  }

  async function signIn(email: string, password: string) {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    return { error: error as Error | null }
  }

  async function signUp(email: string, password: string) {
    const supabase = getSupabase()
    const { error } = await supabase.auth.signUp({ email, password })
    return { error: error as Error | null }
  }

  async function signOut() {
    const supabase = getSupabase()
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signUp, signOut, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
