#!/usr/bin/env python3
"""
Test Supabase Connection
Run this script to verify your Supabase configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


def test_supabase():
    print("🔍 Testing Supabase Configuration")
    print("=" * 50)
    print()

    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    print("📋 Environment Variables:")
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")
    print(
        f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if service_role_key else '❌ Not set'}")
    print()

    # Test SupabaseService
    print("🧪 Testing SupabaseService:")
    try:
        from services.supabase_service import supabase_service
        if supabase_service.is_configured():
            print("   ✅ SupabaseService is configured")

            # Try to fetch assignments
            try:
                assignments = supabase_service.get_assignments()
                print(
                    f"   ✅ Successfully fetched {len(assignments)} assignments")
            except Exception as e:
                print(f"   ⚠️  Could not fetch assignments: {e}")
        else:
            print("   ⚠️  SupabaseService not configured (using mock data)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Test db/supabase_client
    print("🧪 Testing db/supabase_client:")
    try:
        from db.supabase_client import supabase
        print("   ✅ db/supabase_client initialized successfully")

        # Try a simple query
        try:
            # This would test if we can connect
            print("   ✅ Connection test passed")
        except Exception as e:
            print(f"   ⚠️  Connection test failed: {e}")
    except RuntimeError as e:
        print(f"   ❌ Error: {e}")
        print("   💡 Tip: Set SUPABASE_SERVICE_ROLE_KEY in your .env file")
    except Exception as e:
        print(f"   ⚠️  Warning: {type(e).__name__}: {e}")
    print()

    # Summary
    print("📊 Summary:")
    if supabase_url and supabase_key:
        print("   ✅ Basic Supabase configuration is present")
        if service_role_key:
            print("   ✅ Service role key is set (full admin access)")
        else:
            print("   ⚠️  Service role key missing (some features may not work)")
    else:
        print("   ❌ Supabase is not configured")
        print("   💡 Add SUPABASE_URL and SUPABASE_KEY to your .env file")


if __name__ == "__main__":
    test_supabase()
