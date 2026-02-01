"""
Test script to test creating calendar events
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_create_calendar_event():
    """Test creating a calendar event"""
    
    # Get user_id from command line or use a test one
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not user_id:
        print("❌ Please provide a user_id as argument")
        print("Usage: python test_create_calendar_event.py <user_id>")
        return
    
    print(f"🔍 Testing Calendar Event Creation for user: {user_id}\n")
    
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
        print(f"✅ Found calendar tokens")
        
    except Exception as e:
        print(f"❌ Error fetching tokens: {e}")
        return
    
    # Import calendar service
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from services.calendar_service import calendar_service
        
        print(f"\n📅 Testing calendar event creation...")
        
        # Test event details
        test_title = "Test Event - AI Assistant"
        test_start = datetime.now(timezone.utc) + timedelta(days=1, hours=2)  # Tomorrow at 2 hours from now
        test_end = test_start + timedelta(hours=2)
        test_description = "This is a test event created by the AI assistant to verify calendar integration."
        
        print(f"\n📝 Event Details:")
        print(f"   Title: {test_title}")
        print(f"   Start: {test_start}")
        print(f"   End: {test_end}")
        print(f"   Description: {test_description}")
        
        # Create event using calendar service
        print(f"\n🔄 Creating event via calendar_service...")
        event_result = calendar_service.create_event(
            user_id=user_id,
            title=test_title,
            start_time=test_start,
            end_time=test_end,
            description=test_description
        )
        
        print(f"\n📊 Result:")
        print(f"   Status: {event_result.get('status')}")
        print(f"   Event ID: {event_result.get('id')}")
        print(f"   Title: {event_result.get('title')}")
        print(f"   Link: {event_result.get('link', 'N/A')}")
        print(f"   Note: {event_result.get('note', 'N/A')}")
        
        if event_result.get('status') == 'created':
            print(f"\n✅ Event created successfully!")
            if event_result.get('link'):
                print(f"   View in Google Calendar: {event_result.get('link')}")
        elif event_result.get('status') == 'mock_created':
            print(f"\n⚠️  Mock event created (calendar not properly connected)")
        else:
            print(f"\n❌ Failed to create event")
            print(f"   Error: {event_result.get('error', 'Unknown error')}")
        
        # Verify by fetching events
        print(f"\n🔍 Verifying event was created by fetching events...")
        events = calendar_service.get_events(
            user_id=user_id,
            time_min=test_start - timedelta(hours=1),
            time_max=test_end + timedelta(hours=1),
            max_results=10
        )
        
        print(f"   Found {len(events)} events in the time range")
        if events:
            print(f"\n   Events found:")
            for i, event in enumerate(events, 1):
                print(f"   {i}. {event.get('title')} - {event.get('start')}")
                if event.get('id') == event_result.get('id'):
                    print(f"      ✅ This is the event we just created!")
        else:
            print(f"   ⚠️  Event not found in calendar (might be a timezone issue)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_create_calendar_event()

