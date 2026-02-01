-- Create calendar_tokens table in Supabase
-- This table stores Google Calendar OAuth tokens for each user

CREATE TABLE IF NOT EXISTS calendar_tokens (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    refresh_token TEXT NOT NULL,
    access_token TEXT,
    token_uri TEXT DEFAULT 'https://oauth2.googleapis.com/token',
    client_id TEXT,
    client_secret TEXT,
    scopes TEXT[] DEFAULT ARRAY['https://www.googleapis.com/auth/calendar.events'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_calendar_tokens_user_id ON calendar_tokens(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE calendar_tokens ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own tokens
CREATE POLICY "Users can view own calendar tokens"
    ON calendar_tokens FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own tokens
CREATE POLICY "Users can insert own calendar tokens"
    ON calendar_tokens FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own tokens
CREATE POLICY "Users can update own calendar tokens"
    ON calendar_tokens FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own tokens
CREATE POLICY "Users can delete own calendar tokens"
    ON calendar_tokens FOR DELETE
    USING (auth.uid() = user_id);

-- Note: In production, consider encrypting refresh_token before storing
-- You can use pgcrypto extension for encryption:
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- Then encrypt: pgp_sym_encrypt(refresh_token, 'your_encryption_key')

