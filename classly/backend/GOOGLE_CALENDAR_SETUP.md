# Google Calendar API Setup Guide

## Issue
You're seeing this error:
```
Google Calendar API has not been used in project 129628142969 before or it is disabled.
```

This means the Google Calendar API needs to be enabled in your Google Cloud project.

## Solution

### Step 1: Enable Google Calendar API

1. Go to the Google Cloud Console: https://console.cloud.google.com/apis/api/calendar-json.googleapis.com/overview?project=129628142969

   Or manually:
   - Go to https://console.cloud.google.com/
   - Select your project (ID: 129628142969)
   - Navigate to **APIs & Services** → **Library**
   - Search for "Google Calendar API"
   - Click on it and click **Enable**

2. Wait 2-3 minutes for the API to be enabled (Google needs time to propagate)

### Step 2: Verify OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Make sure your app is configured:
   - User Type: External (for testing) or Internal (for Google Workspace)
   - Scopes: Make sure `https://www.googleapis.com/auth/calendar` is added
   - Test users: Add your email if using External type

### Step 3: Verify OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Find your OAuth 2.0 Client ID (the one ending in `.apps.googleusercontent.com`)
3. Make sure:
   - **Authorized redirect URIs** includes: `http://localhost:5000/api/calendar/oauth/callback`
   - The client is enabled

### Step 4: Test the Connection

1. Restart your backend server
2. Go to your app and click "Connect Google Calendar"
3. Complete the OAuth flow
4. Try querying your calendar again

## Quick Enable Link

Click here to enable the Calendar API directly:
**https://console.cloud.google.com/apis/api/calendar-json.googleapis.com/overview?project=129628142969**

Then click the **Enable** button.

## After Enabling

Once enabled:
- Wait 2-3 minutes for propagation
- Restart your backend server
- Reconnect your Google Calendar (if already connected, disconnect and reconnect)
- The calendar fetching should work with real data instead of mock data

## Troubleshooting

### Still getting the error after enabling?
- Wait a few more minutes (Google can take up to 5 minutes)
- Make sure you're using the correct project ID (129628142969)
- Check that the API shows as "Enabled" in the console
- Try disconnecting and reconnecting your calendar

### Getting "accessNotConfigured" error?
- The API is not enabled yet
- Wait longer after enabling
- Make sure you enabled "Google Calendar API" (not just "Calendar API" - there might be multiple)

### OAuth flow not working?
- Check that redirect URI matches exactly: `http://localhost:5000/api/calendar/oauth/callback`
- Verify OAuth consent screen is configured
- Make sure you're using the correct Client ID and Secret in your `.env` file

