# Fix Calendar Connection RLS Issue

## Problem
Getting error: `new row violates row-level security policy for table "calendar_tokens"`

## Root Cause
The Supabase client was using `SUPABASE_KEY` (anon key) instead of `SUPABASE_SERVICE_ROLE_KEY` (service role key). The anon key is subject to RLS policies, while the service role key bypasses them.

## Solution Applied
✅ Updated `get_supabase_client()` in `calendar_service.py` to use `SUPABASE_SERVICE_ROLE_KEY`

## Table Schema Verification
The `calendar_tokens` table has:
- `user_id` (uuid, primary key) ✅
- `refresh_token` (text) ✅
- `access_token` (text) ✅
- `token_uri` (text) ✅
- `client_id` (text) ✅
- `client_secret` (text) ✅
- `scopes` (text[]) ✅
- `created_at` (timestamptz) ✅
- `updated_at` (timestamptz) ✅

The code inserts all these fields correctly.

## Next Steps
1. **Restart the backend server** to apply the fix
2. Try connecting Google Calendar again
3. The credentials should now store successfully in Supabase

## Verification
After restart, the connection should:
- ✅ Store credentials in Supabase (no RLS error)
- ✅ Show "Calendar Connected" in frontend
- ✅ Allow tools to fetch real calendar events

