"""
Quick script to list all users who have connected their calendar
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Supabase credentials not configured")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

try:
    result = supabase.table('calendar_tokens').select('user_id').execute()
    
    if result.data:
        print(f"✅ Found {len(result.data)} user(s) with connected calendars:\n")
        for i, row in enumerate(result.data, 1):
            print(f"   {i}. {row['user_id']}")
        print(f"\nTo test, run:")
        print(f"   python test_calendar_api.py <user_id>")
    else:
        print("❌ No users have connected their calendar yet")
except Exception as e:
    print(f"❌ Error: {e}")

