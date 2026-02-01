# Supabase Setup Guide

This guide will help you configure Supabase for the Classly application.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Your project name (e.g., "Classly")
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to you
5. Wait for the project to be created (takes ~2 minutes)

## Step 2: Get Your Supabase Credentials

Once your project is created:

1. Go to **Settings** → **API** in your Supabase dashboard
2. You'll find:
   - **Project URL** (this is your `SUPABASE_URL`)
   - **anon/public key** (this is your `SUPABASE_KEY` for frontend and `SUPABASE_ANON_KEY`)
   - **service_role key** (this is your `SUPABASE_SERVICE_ROLE_KEY` - keep this secret!)

## Step 3: Configure Backend Environment Variables

1. Create a `.env` file in `classly/backend/` (if it doesn't exist)
2. Add the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Important**: 
- `SUPABASE_URL` is your project URL from the API settings
- `SUPABASE_KEY` is the `anon`/`public` key (used for client-side operations)
- `SUPABASE_SERVICE_ROLE_KEY` is the `service_role` key (used for admin operations - keep secret!)

## Step 4: Configure Frontend Environment Variables

1. Create a `.env.local` file in `classly/` (if it doesn't exist)
2. Add the following variables:

```env
# Supabase Configuration (Frontend)
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Note**: The frontend uses `NEXT_PUBLIC_` prefix so these variables are available in the browser.

## Step 5: Set Up Database Tables

You need to create the following tables in Supabase:

### 1. Assignments Table

Go to **SQL Editor** in Supabase and run:

```sql
-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  course TEXT,
  due_date TIMESTAMPTZ,
  platform TEXT,
  status TEXT DEFAULT 'pending',
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
```

### 2. Calendar Tokens Table

Run the migration file:

```bash
# The SQL is already in: classly/backend/migrations/create_calendar_tokens_table.sql
```

Or copy the SQL from that file and run it in the Supabase SQL Editor.

## Step 6: Test Your Configuration

Run the test script:

```bash
cd classly/backend
source venv/bin/activate
python test_supabase.py
```

This will verify:
- ✅ Environment variables are set
- ✅ Supabase connection works
- ✅ Tables are accessible

## Troubleshooting

### Error: "Missing Supabase environment variables"
- Make sure you created `.env` in `classly/backend/`
- Check that all three variables are set: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

### Error: "Invalid API key"
- Double-check you copied the keys correctly (no extra spaces)
- Make sure you're using the right key:
  - `anon` key for `SUPABASE_KEY` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `service_role` key for `SUPABASE_SERVICE_ROLE_KEY`

### Error: "Table not found"
- Make sure you ran the SQL migrations in the Supabase SQL Editor
- Check that Row Level Security (RLS) policies are created

### Frontend shows "Supabase is not configured"
- Make sure you created `.env.local` in `classly/` (not `classly/backend/`)
- Check that variables start with `NEXT_PUBLIC_`
- Restart the Next.js dev server after adding environment variables

## Security Notes

⚠️ **Important Security Reminders:**

1. **Never commit `.env` or `.env.local` files to git** - they contain secrets!
2. The `service_role` key has admin access - keep it secret and only use it on the backend
3. The `anon` key is safe to use in the frontend (it's restricted by RLS policies)
4. Always use Row Level Security (RLS) policies to protect user data

## Next Steps

Once Supabase is configured:
1. ✅ Test the connection with `python test_supabase.py`
2. ✅ Restart your backend server
3. ✅ Restart your frontend server
4. ✅ Try logging in through the app
5. ✅ Test the AI chat feature (it will use real assignment data)

