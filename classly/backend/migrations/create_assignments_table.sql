-- Create assignments table in Supabase
-- Run this in your Supabase SQL Editor

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  due_at TIMESTAMPTZ,
  url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own assignments
CREATE POLICY "Users can view own assignments"
  ON assignments FOR SELECT
  USING (auth.uid() = user_id);

-- Create policy: Users can insert their own assignments
CREATE POLICY "Users can insert own assignments"
  ON assignments FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update their own assignments
CREATE POLICY "Users can update own assignments"
  ON assignments FOR UPDATE
  USING (auth.uid() = user_id);

-- Create policy: Users can delete their own assignments
CREATE POLICY "Users can delete own assignments"
  ON assignments FOR DELETE
  USING (auth.uid() = user_id);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_assignments_user_id ON assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_due_at ON assignments(due_at);

