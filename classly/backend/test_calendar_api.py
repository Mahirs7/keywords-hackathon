"""
Test script to directly test Google Calendar API calls
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_calendar_api():
    """Test Google Calendar API directly"""
    
    # Get user_id from command line or use a test one
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not user_id:
        print("❌ Please provide a user_id as argument")
        print("Usage: python test_calendar_api.py <user_id>")
        return
    
    print(f"🔍 Testing Calendar API for user: {user_id}\n")
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not configured")
        return
    
    print("✅ Supabase credentials found")
    
    # Connect to Supabase
    supabase = create_client(supabase_url, supabase_key)
    
    # Get calendar tokens
    try:
        print(f"\n📋 Fetching calendar tokens from Supabase...")
        result = supabase.table('calendar_tokens')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            print("❌ No calendar tokens found for this user")
            print("   Please connect your Google Calendar first")
            return
        
        creds_data = result.data[0]
        print(f"✅ Found calendar tokens:")
        print(f"   Has refresh_token: {bool(creds_data.get('refresh_token'))}")
        print(f"   Has access_token: {bool(creds_data.get('access_token') or creds_data.get('token'))}")
        print(f"   Scopes: {creds_data.get('scopes', [])}")
        
    except Exception as e:
        print(f"❌ Error fetching tokens: {e}")
        return
    
    # Create Google Calendar service
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        
        client_id = os.getenv('GOOGLE_CALENDAR_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET')
        
        print(f"\n🔑 Creating Google Calendar credentials...")
        creds = Credentials(
            token=creds_data.get('access_token') or creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=creds_data.get('client_id', client_id),
            client_secret=creds_data.get('client_secret', client_secret),
            scopes=creds_data.get('scopes', ['https://www.googleapis.com/auth/calendar.events'])
        )
        
        # Refresh if expired
        if creds.expired:
            print("🔄 Token expired, refreshing...")
            if creds.refresh_token:
                creds.refresh(Request())
                print("✅ Token refreshed")
            else:
                print("❌ No refresh token available")
                return
        
        print("✅ Credentials created successfully")
        
        # Build service
        print(f"\n🏗️  Building Calendar service...")
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Service created")
        
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test API call
    try:
        print(f"\n📅 Testing API call...")
        
        # Calculate time range for next week
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday()) + timedelta(days=7)
        time_min = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        time_max = week_start + timedelta(days=7)
        
        # Convert to RFC3339 format
        time_min_str = time_min.isoformat().replace('+00:00', 'Z')
        time_max_str = time_max.isoformat().replace('+00:00', 'Z')
        
        print(f"   Time range: {time_min_str} to {time_max_str}")
        print(f"   (Local time: {time_min} to {time_max})")
        
        # Make API call
        print(f"\n🌐 Calling Google Calendar API...")
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min_str,
            timeMax=time_max_str,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"\n📊 Results:")
        print(f"   Total events found: {len(events)}")
        
        if len(events) == 0:
            print("\n⚠️  No events found. Possible reasons:")
            print("   1. No events in this time range")
            print("   2. Timezone mismatch")
            print("   3. Events are in a different calendar")
            print("   4. API permissions issue")
            
            # Try a broader time range
            print(f"\n🔍 Trying broader time range (next 30 days)...")
            time_min_broad = now
            time_max_broad = now + timedelta(days=30)
            time_min_broad_str = time_min_broad.isoformat().replace('+00:00', 'Z')
            time_max_broad_str = time_max_broad.isoformat().replace('+00:00', 'Z')
            
            events_result_broad = service.events().list(
                calendarId='primary',
                timeMin=time_min_broad_str,
                timeMax=time_max_broad_str,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events_broad = events_result_broad.get('items', [])
            print(f"   Events in next 30 days: {len(events_broad)}")
            
            if events_broad:
                print("\n✅ Found events in broader range! Time range might be the issue.")
                for i, event in enumerate(events_broad[:5], 1):
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    title = event.get('summary', 'No title')
                    print(f"   {i}. {title} - {start}")
            else:
                # Try listing all calendars
                print(f"\n🔍 Checking available calendars...")
                try:
                    calendar_list = service.calendarList().list().execute()
                    calendars = calendar_list.get('items', [])
                    print(f"   Found {len(calendars)} calendar(s):")
                    for cal in calendars[:5]:
                        print(f"   - {cal.get('summary', 'Unnamed')} (id: {cal.get('id', 'N/A')})")
                    
                    # Try fetching from all calendars
                    print(f"\n🔍 Trying to fetch events from all calendars...")
                    all_events = []
                    for cal in calendars[:3]:  # Try first 3 calendars
                        cal_id = cal.get('id')
                        try:
                            cal_events = service.events().list(
                                calendarId=cal_id,
                                timeMin=time_min_broad_str,
                                timeMax=time_max_broad_str,
                                maxResults=10,
                                singleEvents=True,
                                orderBy='startTime'
                            ).execute()
                            cal_items = cal_events.get('items', [])
                            if cal_items:
                                print(f"   ✅ Found {len(cal_items)} events in '{cal.get('summary')}' calendar")
                                all_events.extend(cal_items)
                        except Exception as e:
                            print(f"   ⚠️  Error fetching from {cal.get('summary')}: {e}")
                    
                    if all_events:
                        print(f"\n✅ Found {len(all_events)} total events across calendars!")
                        for i, event in enumerate(all_events[:5], 1):
                            start = event['start'].get('dateTime', event['start'].get('date'))
                            title = event.get('summary', 'No title')
                            print(f"   {i}. {title} - {start}")
                    else:
                        print(f"   ⚠️  No events found in any calendar")
                except Exception as e:
                    print(f"   ❌ Error listing calendars: {e}")
        else:
            print(f"\n✅ Found {len(events)} events:")
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                title = event.get('summary', 'No title')
                print(f"   {i}. {title}")
                print(f"      Start: {start}")
                print(f"      End: {end}")
        
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_calendar_api()

