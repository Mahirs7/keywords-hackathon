"""
Google Calendar OAuth Routes
Handles OAuth flow for connecting user's Google Calendar
"""

from flask import Blueprint, request, redirect, jsonify, session
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from services.calendar_service import calendar_service
from utils.auth_helpers import get_user_id_from_request

load_dotenv()

calendar_oauth_bp = Blueprint('calendar_oauth', __name__)

# Google OAuth configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
REDIRECT_URI = os.getenv('GOOGLE_CALENDAR_REDIRECT_URI', 'http://localhost:5000/api/calendar/oauth/callback')


@calendar_oauth_bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    """
    Step 1: Get OAuth URL or redirect to Google consent screen
    GET: Redirects to Google (for direct browser access)
    POST: Returns OAuth URL as JSON (for frontend to handle redirect)
    """
    client_id = os.getenv('GOOGLE_CALENDAR_CLIENT_ID')
    
    if not client_id:
        return jsonify({
            "success": False,
            "error": "Google Calendar OAuth not configured. Set GOOGLE_CALENDAR_CLIENT_ID in .env"
        }), 500
    
    # Get user_id from JWT token (required for OAuth)
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Authentication required. Please log in to connect your Google Calendar."
        }), 401
    
    # Store user_id in session for callback
    session['oauth_user_id'] = user_id
    
    # Build Google OAuth URL
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',  # Required to get refresh token
        'prompt': 'consent',  # Force consent screen to get refresh token
        'state': user_id  # Pass user_id in state for security
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    # If POST request, return URL as JSON (for frontend to handle redirect)
    if request.method == 'POST':
        return jsonify({
            "success": True,
            "auth_url": auth_url
        })
    
    # If GET request, redirect directly (for browser access)
    return redirect(auth_url)


@calendar_oauth_bp.route('/oauth/callback', methods=['GET'])
def callback():
    """
    Step 2: Handle OAuth callback and exchange code for tokens
    """
    error = request.args.get('error')
    if error:
        return jsonify({
            "success": False,
            "error": f"OAuth error: {error}"
        }), 400
    
    code = request.args.get('code')
    state = request.args.get('state')  # user_id from state
    
    if not code:
        return jsonify({
            "success": False,
            "error": "Authorization code not provided"
        }), 400
    
    # Get user_id from state or session
    user_id = state or session.get('oauth_user_id')
    
    # Force flush output to see logs immediately
    import sys
    print(f"🔍 OAuth Callback - state: {state}, session user_id: {session.get('oauth_user_id')}, extracted user_id: {user_id}", flush=True)
    sys.stdout.flush()
    
    if not user_id:
        # Try to get from JWT token as fallback
        user_id = get_user_id_from_request()
        print(f"🔍 Tried JWT fallback, user_id: {user_id}", flush=True)
        sys.stdout.flush()
    
    if not user_id:
        print("❌ No user_id found in callback", flush=True)
        sys.stdout.flush()
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/ai?calendar_error=Authentication required. Please log in first.")
    
    print(f"✅ Using user_id: {user_id}", flush=True)
    sys.stdout.flush()
    
    try:
        # Exchange authorization code for tokens
        print("🔄 Exchanging authorization code for tokens...", flush=True)
        sys.stdout.flush()
        tokens = calendar_service.exchange_code_for_tokens(code, REDIRECT_URI)
        print(f"✅ Successfully exchanged code for tokens. Has refresh_token: {bool(tokens.get('refresh_token'))}", flush=True)
        sys.stdout.flush()
        
        # Store tokens for this user
        print(f"💾 Storing credentials for user {user_id}...", flush=True)
        sys.stdout.flush()
        calendar_service.store_user_credentials(user_id, tokens)
        print(f"✅ Credentials stored for user {user_id}", flush=True)
        sys.stdout.flush()
        
        # Redirect to frontend success page
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/ai?calendar_connected=true")
        
    except Exception as e:
        print(f"❌ Error in OAuth callback: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/ai?calendar_error={str(e)}")


@calendar_oauth_bp.route('/oauth/status', methods=['GET'])
def get_connection_status():
    """
    Check if user has connected their Google Calendar
    """
    # Get user_id from JWT token
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Authentication required. Please log in."
        }), 401
    
    is_connected = calendar_service.is_user_connected(user_id)
    
    return jsonify({
        "success": True,
        "connected": is_connected,
        "user_id": user_id
    })


@calendar_oauth_bp.route('/oauth/disconnect', methods=['POST'])
def disconnect():
    """
    Disconnect user's Google Calendar
    """
    # Get user_id from JWT token
    user_id = get_user_id_from_request()
    
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Authentication required. Please log in."
        }), 401
    
    calendar_service.revoke_user_credentials(user_id)
    
    return jsonify({
        "success": True,
        "message": "Google Calendar disconnected successfully"
    })

