import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://xieyimjykzccrjmlqdps.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpZXlpbWp5a3pjY3JqbWxxZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxNTE2NjcsImV4cCI6MjA4MzcyNzY2N30.lJtGhgJdPld5GTG_F6So7Gi-cRzzAcE3QXTqQJsEBeM'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for our database
export interface VisitorLog {
  id: string
  created_at: string
  path: string
  user_agent: string
  ip_address?: string
  referrer?: string
  country?: string
}

export interface UserProfile {
  id: string
  email: string
  created_at: string
  last_sign_in: string
  role: 'user' | 'admin'
}

// Log a page visit
export async function logVisit(path: string, userAgent: string, referrer?: string) {
  try {
    const { error } = await supabase
      .from('visitor_logs')
      .insert({
        path,
        user_agent: userAgent,
        referrer: referrer || null,
      })
    if (error) console.error('Error logging visit:', error)
  } catch (e) {
    console.error('Failed to log visit:', e)
  }
}

// Get visitor stats
export async function getVisitorStats() {
  const { data, error } = await supabase
    .from('visitor_logs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(1000)

  if (error) {
    console.error('Error fetching visitor stats:', error)
    return null
  }
  return data
}

// Get all users (admin only)
export async function getUsers() {
  const { data, error } = await supabase
    .from('user_profiles')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching users:', error)
    return null
  }
  return data
}
