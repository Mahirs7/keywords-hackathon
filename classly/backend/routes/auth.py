"""
Authentication API Routes
User authentication and session management
"""

from flask import Blueprint, jsonify, request
import os

auth_bp = Blueprint('auth', __name__)

# Mock user data
MOCK_USER = {
    "id": "user_123",
    "name": "Alex",
    "email": "alex@illinois.edu",
    "avatar": None,
    "university": "University of Illinois Urbana-Champaign",
    "created_at": "2026-01-15T10:00:00Z",
    "preferences": {
        "theme": "dark",
        "notifications": True,
        "study_reminder_time": "09:00"
    },
    "connected_platforms": ["canvas", "gradescope", "campuswire", "prairielearn"]
}


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user profile"""
    return jsonify({
        "success": True,
        "data": MOCK_USER
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email/password or SSO"""
    data = request.get_json()
    
    # Mock login - in production would verify with Supabase Auth
    return jsonify({
        "success": True,
        "data": {
            "user": MOCK_USER,
            "access_token": "mock_jwt_token_123",
            "refresh_token": "mock_refresh_token_456"
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user"""
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@auth_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    return jsonify({
        "success": True,
        "data": MOCK_USER["preferences"]
    })


@auth_bp.route('/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    data = request.get_json()
    
    # Mock update - in production would save to Supabase
    updated_prefs = {**MOCK_USER["preferences"], **data}
    
    return jsonify({
        "success": True,
        "data": updated_prefs,
        "message": "Preferences updated"
    })
