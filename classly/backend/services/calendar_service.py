"""
Google Calendar Service
Handles Google Calendar integration for creating events
Uses per-user OAuth credentials stored in Supabase
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase client for storing tokens
_supabase_client = None


def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client for storing calendar tokens
    Uses SERVICE_ROLE_KEY to bypass RLS policies (backend operations)
    """
    global _supabase_client
    supabase_url = os.getenv('SUPABASE_URL')
    # Use SERVICE_ROLE_KEY to bypass RLS for backend operations
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    # Debug: Check which key is being used
    if supabase_key:
        key_preview = supabase_key[:20] + \
            "..." if len(supabase_key) > 20 else supabase_key
        print(f"🔑 Using SUPABASE_SERVICE_ROLE_KEY (preview: {key_preview})")
    else:
        print("⚠️  SUPABASE_SERVICE_ROLE_KEY not found in environment!")
        # Fallback check for old variable name
        fallback_key = os.getenv('SUPABASE_KEY')
        if fallback_key:
            print(
                "⚠️  Found SUPABASE_KEY instead - this is the ANON key and will hit RLS!")
            print("⚠️  Please set SUPABASE_SERVICE_ROLE_KEY in your .env file")

    if not supabase_url or not supabase_key:
        print(
            f"❌ Missing Supabase config - URL: {bool(supabase_url)}, Key: {bool(supabase_key)}")
        return None

    # Always recreate client to ensure we're using the latest key
    # This ensures we use SERVICE_ROLE_KEY even if client was created before
    _supabase_client = create_client(supabase_url, supabase_key)
    print(f"✅ Created Supabase client with SERVICE_ROLE_KEY (should bypass RLS)")
    return _supabase_client


class CalendarService:
    """Service for interacting with Google Calendar with per-user authentication"""

    def __init__(self):
        # These are app-level OAuth credentials (not user-specific)
        # Users will authenticate individually via OAuth flow
        self.client_id = os.getenv('GOOGLE_CALENDAR_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET')
        self.redirect_uri = os.getenv(
            'GOOGLE_CALENDAR_REDIRECT_URI', 'http://localhost:5000/api/calendar/oauth/callback')

    def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Dictionary with tokens and credentials
        """
        try:
            from google_auth_oauthlib.flow import Flow
            from google.oauth2.credentials import Credentials

            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=['https://www.googleapis.com/auth/calendar.events']
            )
            flow.redirect_uri = redirect_uri

            # Exchange code for tokens
            flow.fetch_token(code=code)

            credentials = flow.credentials

            print(f"🔑 Token exchange successful:")
            print(f"   Has token: {bool(credentials.token)}")
            print(f"   Has refresh_token: {bool(credentials.refresh_token)}")
            print(f"   Token URI: {credentials.token_uri}")
            print(f"   Scopes: {credentials.scopes}")

            if not credentials.refresh_token:
                print(
                    "⚠️  WARNING: No refresh_token received. User may need to re-authorize with prompt=consent")

            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
        except Exception as e:
            print(f"❌ Error exchanging code for tokens: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error exchanging code for tokens: {str(e)}")

    def store_user_credentials(self, user_id: str, credentials: Dict[str, Any]):
        """
        Store user's Google Calendar credentials in Supabase

        Args:
            user_id: Supabase user ID
            credentials: OAuth tokens and credentials
        """
        # Check if user_id is a valid UUID before querying Supabase
        is_valid_uuid = False
        try:
            import uuid
            uuid.UUID(user_id)
            is_valid_uuid = True
        except (ValueError, AttributeError):
            # Not a valid UUID, skip Supabase query
            pass

        supabase = get_supabase_client()

        if supabase and is_valid_uuid:
            try:
                # Store in 'calendar_tokens' table
                # Table schema: user_id (uuid, primary key), refresh_token (text, encrypted),
                # access_token (text), token_uri (text), expires_at (timestamp), created_at (timestamp)

                print(
                    f"💾 Attempting to store credentials in Supabase for user {user_id}...")
                print(
                    f"   Has refresh_token: {bool(credentials.get('refresh_token'))}")
                print(f"   Has access_token: {bool(credentials.get('token'))}")

                # Check for refresh_token (required field - NOT NULL in table)
                refresh_token = credentials.get('refresh_token')
                if not refresh_token:
                    error_msg = "No refresh_token received from Google. User needs to re-authorize with prompt=consent."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg)

                # Prepare data for upsert
                data = {
                    'user_id': user_id,
                    'refresh_token': refresh_token,
                    'access_token': credentials.get('token'),
                    'token_uri': credentials.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    'client_id': credentials.get('client_id', self.client_id),
                    'client_secret': credentials.get('client_secret', self.client_secret),
                    'scopes': credentials.get('scopes', ['https://www.googleapis.com/auth/calendar.events'])
                }

                print(f"   Data keys: {list(data.keys())}")
                print(f"   refresh_token length: {len(refresh_token)}")

                # Upsert (insert or update) the credentials
                result = supabase.table(
                    'calendar_tokens').upsert(data).execute()

                print(
                    f"✅ Successfully stored calendar credentials for user {user_id} in Supabase")
                print(
                    f"   Result: {result.data if hasattr(result, 'data') else 'No data returned'}")
            except Exception as e:
                print(f"❌ Error storing credentials in Supabase: {e}")
                # Fallback to in-memory storage
                if not hasattr(self, '_user_credentials'):
                    self._user_credentials = {}
                self._user_credentials[user_id] = credentials
                print(
                    f"⚠️  Stored credentials in-memory as fallback for user {user_id}")
        else:
            # Fallback to in-memory storage if Supabase not configured or invalid UUID
            if not hasattr(self, '_user_credentials'):
                self._user_credentials = {}
            self._user_credentials[user_id] = credentials
            if not is_valid_uuid:
                print(
                    f"Warning: user_id '{user_id}' is not a valid UUID. Storing credentials in-memory only.")
            else:
                print(
                    f"Warning: Supabase not configured. Storing credentials in-memory for user {user_id}")

    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has connected their Google Calendar"""
        # Check if user_id is a valid UUID format
        # If not, skip Supabase query and use in-memory check only
        is_valid_uuid = False
        try:
            import uuid
            uuid.UUID(user_id)
            is_valid_uuid = True
        except (ValueError, AttributeError):
            # Not a valid UUID, skip Supabase query
            pass

        supabase = get_supabase_client()

        if supabase and is_valid_uuid:
            try:
                result = supabase.table('calendar_tokens')\
                    .select('user_id')\
                    .eq('user_id', user_id)\
                    .execute()
                is_connected = len(result.data) > 0
                if is_connected:
                    print(
                        f"✅ User {user_id} has calendar connected (found in Supabase)")
                return is_connected
            except Exception as e:
                print(f"⚠️  Error checking connection in Supabase: {e}")
                # Fallback to in-memory check
                in_memory = hasattr(
                    self, '_user_credentials') and user_id in self._user_credentials
                if in_memory:
                    print(
                        f"✅ User {user_id} has calendar connected (found in-memory)")
                return in_memory
        else:
            # Fallback to in-memory check (for non-UUID user_ids or when Supabase not available)
            in_memory = hasattr(
                self, '_user_credentials') and user_id in self._user_credentials
            if in_memory:
                print(
                    f"✅ User {user_id} has calendar connected (found in-memory)")
            return in_memory

    def revoke_user_credentials(self, user_id: str):
        """Revoke and remove user's Google Calendar credentials"""
        # Check if user_id is a valid UUID before querying Supabase
        is_valid_uuid = False
        try:
            import uuid
            uuid.UUID(user_id)
            is_valid_uuid = True
        except (ValueError, AttributeError):
            # Not a valid UUID, skip Supabase query
            pass

        supabase = get_supabase_client()

        if supabase and is_valid_uuid:
            try:
                supabase.table('calendar_tokens')\
                    .delete()\
                    .eq('user_id', user_id)\
                    .execute()
                print(
                    f"Revoked calendar credentials for user {user_id} from Supabase")
            except Exception as e:
                print(f"Error revoking credentials in Supabase: {e}")
            finally:
                # Also remove from in-memory storage
                if hasattr(self, '_user_credentials') and user_id in self._user_credentials:
                    del self._user_credentials[user_id]
        else:
            # Fallback to in-memory removal
            if hasattr(self, '_user_credentials') and user_id in self._user_credentials:
                del self._user_credentials[user_id]

    def get_user_service(self, user_id: str):
        """
        Get Google Calendar service for a specific user

        Args:
            user_id: Supabase user ID to get credentials for

        Returns:
            Google Calendar service instance or None if not authenticated
        """
        import sys
        print(f"🔧 get_user_service called for user {user_id}", flush=True)
        sys.stdout.flush()

        if not self.is_user_connected(user_id):
            print(f"⚠️  User {user_id} is not connected", flush=True)
            sys.stdout.flush()
            return None

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            # Get credentials from Supabase
            supabase = get_supabase_client()
            creds_data = None

            # Check if user_id is a valid UUID before querying Supabase
            is_valid_uuid = False
            try:
                import uuid
                uuid.UUID(user_id)
                is_valid_uuid = True
            except (ValueError, AttributeError):
                # Not a valid UUID, skip Supabase query
                print(f"⚠️  User ID {user_id} is not a valid UUID", flush=True)
                sys.stdout.flush()
                pass

            if supabase and is_valid_uuid:
                try:
                    print(
                        f"🔍 Fetching credentials from Supabase for user {user_id}...", flush=True)
                    sys.stdout.flush()
                    result = supabase.table('calendar_tokens')\
                        .select('*')\
                        .eq('user_id', user_id)\
                        .execute()

                    if result.data and len(result.data) > 0:
                        creds_data = result.data[0]
                        print(
                            f"✅ Found credentials in Supabase (has refresh_token: {bool(creds_data.get('refresh_token'))})", flush=True)
                        sys.stdout.flush()
                    else:
                        print(
                            f"⚠️  No credentials found in Supabase for user {user_id}", flush=True)
                        sys.stdout.flush()
                except Exception as e:
                    print(
                        f"❌ Error fetching credentials from Supabase: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    sys.stdout.flush()

            # Fallback to in-memory storage
            if not creds_data and hasattr(self, '_user_credentials') and user_id in self._user_credentials:
                print(
                    f"📦 Using in-memory credentials for user {user_id}", flush=True)
                sys.stdout.flush()
                creds_data = self._user_credentials[user_id]

            if not creds_data:
                print(f"❌ No credentials found for user {user_id}", flush=True)
                sys.stdout.flush()
                return None

            print(f"🔑 Creating Credentials object...", flush=True)
            sys.stdout.flush()
            creds = Credentials(
                token=creds_data.get(
                    'access_token') or creds_data.get('token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get(
                    'token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=creds_data.get('client_id', self.client_id),
                client_secret=creds_data.get(
                    'client_secret', self.client_secret),
                scopes=creds_data.get(
                    'scopes', ['https://www.googleapis.com/auth/calendar.events'])
            )

            # Refresh token if expired
            if creds.expired:
                print(f"🔄 Token expired, refreshing...", flush=True)
                sys.stdout.flush()
                if creds.refresh_token:
                    creds.refresh(Request())
                    print(f"✅ Token refreshed successfully", flush=True)
                    sys.stdout.flush()
                    # Update stored credentials in Supabase
                    if supabase:
                        try:
                            supabase.table('calendar_tokens').update({
                                'access_token': creds.token,
                                'refresh_token': creds.refresh_token
                            }).eq('user_id', user_id).execute()
                            print(
                                f"✅ Updated refreshed token in Supabase", flush=True)
                            sys.stdout.flush()
                        except Exception as e:
                            print(
                                f"⚠️  Error updating refreshed token in Supabase: {e}", flush=True)
                            sys.stdout.flush()
                    # Also update in-memory if exists
                    if hasattr(self, '_user_credentials') and user_id in self._user_credentials:
                        self._user_credentials[user_id]['token'] = creds.token
                        self._user_credentials[user_id]['refresh_token'] = creds.refresh_token
                else:
                    print(f"❌ Token expired but no refresh_token available", flush=True)
                    sys.stdout.flush()
            else:
                print(f"✅ Token is still valid", flush=True)
                sys.stdout.flush()

            print(f"🏗️  Building Calendar service...", flush=True)
            sys.stdout.flush()
            service = build('calendar', 'v3', credentials=creds)
            print(f"✅ Calendar service created successfully", flush=True)
            sys.stdout.flush()
            return service
        except Exception as e:
            print(
                f"❌ Error creating calendar service for user {user_id}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            return None

    def is_configured(self) -> bool:
        """Check if Google Calendar OAuth is properly configured"""
        return self.client_id is not None and self.client_secret is not None

    def create_event(
        self,
        user_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a calendar event for a specific user

        Args:
            user_id: User ID who owns the calendar
            title: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description (optional)
            location: Event location (optional)

        Returns:
            Dictionary with event details
        """
        if not self.is_user_connected(user_id):
            # Return mock event with note about connecting calendar
            return self._create_mock_event(
                title, start_time, end_time, description, location,
                note="Please connect your Google Calendar to create real events."
            )

        service = self.get_user_service(user_id)
        if not service:
            return self._create_mock_event(
                title, start_time, end_time, description, location,
                note="Error accessing your Google Calendar. Please reconnect."
            )

        try:
            from datetime import timezone as tz

            # Ensure timezone-aware datetimes (should already be UTC)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=tz.utc)
            else:
                start_time = start_time.astimezone(tz.utc)

            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=tz.utc)
            else:
                end_time = end_time.astimezone(tz.utc)

            # Format as RFC3339 for Google Calendar API
            start_str = start_time.isoformat().replace('+00:00', 'Z')
            end_str = end_time.isoformat().replace('+00:00', 'Z')

            # Use provided timezone or default to UTC
            # Google Calendar will display the event in this timezone
            # Default to a common US timezone
            event_timezone = timezone if timezone else 'America/Chicago'

            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_str,
                    'timeZone': event_timezone,
                },
                'end': {
                    'dateTime': end_str,
                    'timeZone': event_timezone,
                },
            }

            print(f"📅 Creating event with:")
            print(f"   Start: {start_str} (UTC)")
            print(f"   End: {end_str} (UTC)")
            print(f"   Display Timezone: {event_timezone}")
            import sys
            sys.stdout.flush()

            if location:
                event['location'] = location

            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return {
                'id': created_event.get('id'),
                'title': created_event.get('summary'),
                'start': created_event.get('start'),
                'end': created_event.get('end'),
                'link': created_event.get('htmlLink'),
                'status': 'created'
            }
        except Exception as e:
            print(f"Error creating calendar event for user {user_id}: {e}")
            # Fallback to mock
            return self._create_mock_event(
                title, start_time, end_time, description, location,
                note=f"Error: {str(e)}"
            )

    def get_events(
        self,
        user_id: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events for a specific user

        Args:
            user_id: User ID who owns the calendar
            time_min: Start time for events (defaults to now)
            time_max: End time for events (defaults to 7 days from now)
            max_results: Maximum number of events to return

        Returns:
            List of event dictionaries. Returns empty list if calendar not connected or on error.
            Raises exception with error message if calendar is connected but API call fails.
        """
        import sys
        print(f"📅 get_events called for user {user_id}", flush=True)
        sys.stdout.flush()

        if not self.is_user_connected(user_id):
            print(f"⚠️  Calendar not connected for user {user_id}", flush=True)
            sys.stdout.flush()
            # Calendar not connected - return empty list (no mock data)
            return []

        print(
            f"✅ Calendar is connected for user {user_id}, getting service...", flush=True)
        sys.stdout.flush()

        service = self.get_user_service(user_id)
        if not service:
            print(
                f"❌ Failed to get calendar service for user {user_id}", flush=True)
            sys.stdout.flush()
            # Service creation failed - return empty list (no mock data)
            return []

        try:
            from datetime import timezone

            if not time_min:
                time_min = datetime.now(timezone.utc)
            else:
                # Ensure timezone-aware datetime
                if time_min.tzinfo is None:
                    # Naive datetime - assume it's in local timezone, convert to UTC
                    import time
                    local_tz = time.tzname[0] if time.daylight == 0 else time.tzname[1]
                    # For simplicity, convert naive datetime to UTC
                    # This assumes the datetime is in the system's local timezone
                    time_min = time_min.replace(tzinfo=timezone.utc)
                else:
                    # Already timezone-aware, convert to UTC
                    time_min = time_min.astimezone(timezone.utc)

            if not time_max:
                time_max = time_min + timedelta(days=7)
            else:
                # Ensure timezone-aware datetime
                if time_max.tzinfo is None:
                    time_max = time_max.replace(tzinfo=timezone.utc)
                else:
                    time_max = time_max.astimezone(timezone.utc)

            # Format as RFC3339 (required by Google Calendar API)
            time_min_str = time_min.isoformat().replace('+00:00', 'Z')
            time_max_str = time_max.isoformat().replace('+00:00', 'Z')

            print(
                f"🔍 Fetching events from {time_min_str} to {time_max_str}", flush=True)
            print(
                f"   (time_min: {time_min}, time_max: {time_max})", flush=True)
            sys.stdout.flush()

            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min_str,
                timeMax=time_max_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            print(
                f"📊 Found {len(events)} events from Google Calendar API", flush=True)
            sys.stdout.flush()

            result = []
            for event in events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                event_data = {
                    'id': event.get('id'),
                    'title': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'status': event.get('status', 'confirmed')
                }
                result.append(event_data)
                print(
                    f"   📌 Event: {event_data['title']} at {start}", flush=True)
                sys.stdout.flush()

            print(f"✅ Returning {len(result)} events", flush=True)
            sys.stdout.flush()
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error fetching calendar events: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()

            # Check if it's an API not enabled error
            if "accessNotConfigured" in error_msg or "API has not been used" in error_msg:
                error_detail = "Google Calendar API is not enabled. Please enable it in Google Cloud Console, then reconnect your calendar."
                print("⚠️  " + error_detail, flush=True)
                print(
                    "   https://console.cloud.google.com/apis/api/calendar-json.googleapis.com/overview?project=129628142969", flush=True)
                sys.stdout.flush()
                # Raise exception with clear error message instead of returning mock data
                raise Exception(error_detail)

            # For other errors, raise the exception so the caller can handle it
            raise Exception(f"Failed to fetch calendar events: {error_msg}")

    def _get_mock_events(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Return mock calendar events for development"""
        if not time_min:
            time_min = datetime.now()
        if not time_max:
            time_max = time_min + timedelta(days=7)

        # Generate mock events within the requested time range
        mock_events = []
        days_ahead = 0

        # Ensure we have events in the requested range
        while len(mock_events) < max_results and days_ahead < 7:
            event_date = time_min + timedelta(days=days_ahead)

            # Skip if outside requested range
            if event_date > time_max:
                break

            # Create events at different times
            for hour_offset in [9, 14, 16]:  # 9am, 2pm, 4pm
                if len(mock_events) >= max_results:
                    break

                event_start = event_date.replace(
                    hour=hour_offset, minute=0, second=0, microsecond=0)
                event_end = event_start + timedelta(hours=2)

                # Skip if outside requested range
                if event_start > time_max:
                    continue

                event_titles = [
                    'CS 101 Lecture',
                    'Study Session',
                    'Project Meeting',
                    'Group Work',
                    'Office Hours'
                ]
                event_locations = ['Siebel 1404',
                                   'Library', 'Zoom', 'Online', '']
                event_descriptions = [
                    'Introduction to Computer Science',
                    'Review for upcoming exam',
                    'Discuss project progress',
                    'Collaborative work session',
                    'Q&A session with professor'
                ]

                idx = len(mock_events) % len(event_titles)
                mock_events.append({
                    'id': f'mock_{len(mock_events) + 1}',
                    'title': event_titles[idx],
                    'start': event_start.isoformat(),
                    'end': event_end.isoformat(),
                    'description': event_descriptions[idx],
                    'location': event_locations[idx],
                    'status': 'confirmed'
                })

            days_ahead += 1

        # If no events generated, create at least one
        if not mock_events:
            mock_events.append({
                'id': 'mock_1',
                'title': 'Sample Event',
                'start': time_min.isoformat(),
                'end': (time_min + timedelta(hours=2)).isoformat(),
                'description': 'This is mock data. Connect your Google Calendar to see real events.',
                'location': '',
                'status': 'confirmed'
            })

        return mock_events[:max_results]

    def _create_mock_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a mock event for development"""
        return {
            'id': f'mock_event_{int(datetime.now().timestamp())}',
            'title': title,
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'description': description or '',
            'location': location or '',
            'link': None,
            'status': 'mock_created',
            'note': note or 'This is a mock event. Connect your Google Calendar to create real events.'
        }

    def get_available_slots(
        self,
        date: datetime,
        duration_hours: float = 2.0
    ) -> List[Dict[str, datetime]]:
        """
        Get available time slots for a given date
        This is a simplified version - in production, you'd query actual calendar

        Args:
            date: Date to find slots for
            duration_hours: Duration of needed slot

        Returns:
            List of available time slots
        """
        # Mock implementation - returns some default available slots
        slots = []
        base_time = date.replace(hour=9, minute=0, second=0, microsecond=0)

        for i in range(4):  # 4 slots per day
            start = base_time + timedelta(hours=i*3)
            end = start + timedelta(hours=duration_hours)
            slots.append({
                'start': start,
                'end': end
            })

        return slots


# Singleton instance
calendar_service = CalendarService()
