-- Supabase Setup Script for fault.watch Admin Panel
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)

-- 1. Create visitor_logs table for tracking page visits
CREATE TABLE IF NOT EXISTS visitor_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  path TEXT NOT NULL,
  user_agent TEXT,
  ip_address TEXT,
  referrer TEXT,
  country TEXT
);

-- 2. Create user_profiles table for storing user roles
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_sign_in TIMESTAMP WITH TIME ZONE,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE visitor_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 4. Create policies for visitor_logs
-- Allow anyone to insert (for tracking)
CREATE POLICY "Allow anonymous inserts" ON visitor_logs
  FOR INSERT WITH CHECK (true);

-- Only admins can read visitor logs
CREATE POLICY "Admins can read visitor logs" ON visitor_logs
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.id = auth.uid()
      AND user_profiles.role = 'admin'
    )
  );

-- 5. Create policies for user_profiles
-- Users can read their own profile
CREATE POLICY "Users can read own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

-- Admins can read all profiles
CREATE POLICY "Admins can read all profiles" ON user_profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_profiles.id = auth.uid()
      AND user_profiles.role = 'admin'
    )
  );

-- 6. Create function to auto-create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, created_at)
  VALUES (NEW.id, NEW.email, NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Create trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 8. Create function to update last_sign_in
CREATE OR REPLACE FUNCTION public.handle_user_sign_in()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.user_profiles
  SET last_sign_in = NOW()
  WHERE id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Create index for faster queries
CREATE INDEX IF NOT EXISTS visitor_logs_created_at_idx ON visitor_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS visitor_logs_path_idx ON visitor_logs(path);

-- 10. IMPORTANT: Create your admin user
-- After running this script:
-- 1. Go to Authentication > Users in Supabase dashboard
-- 2. Click "Add user" and create an account with your email
-- 3. Then run this query to make yourself an admin (replace with your email):
--
-- UPDATE user_profiles SET role = 'admin' WHERE email = 'your-email@example.com';

SELECT 'Setup complete! Remember to create an admin user.' as message;
