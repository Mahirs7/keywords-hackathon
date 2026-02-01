-- StudyHub Supabase Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PROFILES (extends auth.users)
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT,
  email TEXT,
  avatar_url TEXT,
  university TEXT DEFAULT 'UIUC',
  preferences JSONB DEFAULT '{}',
  msft_email TEXT,  -- Microsoft/Illinois SSO email for scraping
  msft_password TEXT,  -- Encrypted Microsoft password for scraping
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- USER PLATFORM CONNECTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS user_platforms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('canvas', 'gradescope', 'campuswire', 'prairielearn')),
  connected BOOLEAN DEFAULT false,
  last_synced TIMESTAMPTZ,
  sync_status TEXT DEFAULT 'never' CHECK (sync_status IN ('never', 'syncing', 'success', 'failed')),
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, platform)
);

-- ============================================
-- COURSES
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  platform_course_id TEXT,
  name TEXT NOT NULL,
  department TEXT,
  course_number TEXT,
  section TEXT,
  crn TEXT,
  schedule JSONB, -- {days: ['Mon', 'Wed'], time: '10:00 AM - 11:15 AM', location: 'Siebel 1404'}
  instructor TEXT,
  color TEXT DEFAULT '#3b82f6',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, platform, platform_course_id)
);

-- ============================================
-- DEADLINES (assignments, quizzes, etc.)
-- ============================================
CREATE TABLE IF NOT EXISTS deadlines (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
  platform TEXT NOT NULL,
  platform_assignment_id TEXT,
  title TEXT NOT NULL,
  course_name TEXT, -- denormalized for quick display
  type TEXT DEFAULT 'assignment', -- 'assignment', 'quiz', 'discussion', 'exam', 'lab'
  due_date TIMESTAMPTZ,
  due_date_text TEXT, -- original text like "Feb 4, 11:59 PM"
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'graded', 'late', 'missing')),
  points_possible NUMERIC,
  points_earned NUMERIC,
  url TEXT,
  instructions_text TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, platform, platform_assignment_id)
);

-- ============================================
-- SCHEDULE ITEMS
-- ============================================
CREATE TABLE IF NOT EXISTS schedule_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  type TEXT DEFAULT 'class' CHECK (type IN ('class', 'study', 'break', 'office_hours', 'exam', 'other')),
  start_time TIME,
  end_time TIME,
  duration_minutes INTEGER,
  location TEXT,
  color TEXT DEFAULT '#3b82f6',
  recurring BOOLEAN DEFAULT false,
  days TEXT[], -- ['Monday', 'Wednesday', 'Friday']
  specific_date DATE, -- for one-off events
  related_deadline_id UUID REFERENCES deadlines(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SCRAPE JOBS (track sync status)
-- ============================================
CREATE TABLE IF NOT EXISTS scrape_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  items_synced INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE deadlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;

-- Profiles: users can only see/edit their own profile
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- User platforms: users can only see/edit their own connections
CREATE POLICY "Users can view own platforms" ON user_platforms
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own platforms" ON user_platforms
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own platforms" ON user_platforms
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own platforms" ON user_platforms
  FOR DELETE USING (auth.uid() = user_id);

-- Courses: users can only see/edit their own courses
CREATE POLICY "Users can view own courses" ON courses
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own courses" ON courses
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own courses" ON courses
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own courses" ON courses
  FOR DELETE USING (auth.uid() = user_id);

-- Deadlines: users can only see/edit their own deadlines
CREATE POLICY "Users can view own deadlines" ON deadlines
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own deadlines" ON deadlines
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own deadlines" ON deadlines
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own deadlines" ON deadlines
  FOR DELETE USING (auth.uid() = user_id);

-- Schedule items: users can only see/edit their own schedule
CREATE POLICY "Users can view own schedule" ON schedule_items
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own schedule" ON schedule_items
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own schedule" ON schedule_items
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own schedule" ON schedule_items
  FOR DELETE USING (auth.uid() = user_id);

-- Scrape jobs: users can only see their own jobs
CREATE POLICY "Users can view own scrape jobs" ON scrape_jobs
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own scrape jobs" ON scrape_jobs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_deadlines_user_due ON deadlines(user_id, due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_user_platform ON deadlines(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_courses_user ON courses(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_user ON schedule_items(user_id);
CREATE INDEX IF NOT EXISTS idx_scrape_jobs_user ON scrape_jobs(user_id, created_at DESC);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Get platform summary counts for a user
CREATE OR REPLACE FUNCTION get_platform_summaries(p_user_id UUID)
RETURNS TABLE (
  platform TEXT,
  pending_count BIGINT,
  connected BOOLEAN,
  last_synced TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    up.platform,
    COALESCE(d.cnt, 0) as pending_count,
    up.connected,
    up.last_synced
  FROM user_platforms up
  LEFT JOIN (
    SELECT d.platform, COUNT(*) as cnt
    FROM deadlines d
    WHERE d.user_id = p_user_id 
      AND d.status = 'pending'
      AND d.due_date > NOW()
    GROUP BY d.platform
  ) d ON d.platform = up.platform
  WHERE up.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
