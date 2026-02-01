# Quick Fix Guide

## Issue 1: Google Calendar API Not Enabled

**Error:** `Google Calendar API has not been used in project 129628142969 before or it is disabled`

**Fix:**
1. Click this link: https://console.cloud.google.com/apis/api/calendar-json.googleapis.com/overview?project=129628142969
2. Click the **Enable** button
3. Wait 2-3 minutes
4. Restart your backend server
5. Reconnect your Google Calendar in the app

**Why mock data?** The code catches the API error and returns mock data so the app doesn't crash. Once you enable the API, it will use real calendar data.

---

## Issue 2: Assignments Table Missing

**Error:** `Could not find the table 'public.assignments' in the schema cache`

**Fix:**
1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **SQL Editor**
4. Copy and paste the SQL from `classly/backend/migrations/create_assignments_table.sql`
5. Click **Run**
6. The table will be created with proper security policies

**Why mock data?** The code falls back to mock data when the table doesn't exist. Once you create the table, it will fetch real assignment data.

---

## Summary

You don't need more tools - the tools are working fine! You just need to:

1. ✅ **Enable Google Calendar API** (takes 2-3 minutes)
2. ✅ **Create the assignments table** in Supabase (takes 30 seconds)

After both are done, restart your servers and everything will use real data instead of mock data.

