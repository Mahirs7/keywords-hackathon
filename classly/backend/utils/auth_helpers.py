"""
Authentication Helper Functions
Extract user ID from Supabase JWT tokens
"""

from flask import request
from typing import Optional
import jwt
import os

def get_user_id_from_request() -> Optional[str]:
    """
    Extract user ID from request headers (JWT token from Supabase Auth)
    
    Returns:
        User ID (UUID) string or None if not found
    """
    # Try to get token from Authorization header
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Decode JWT token (Supabase uses HS256)
            # In production, verify with Supabase JWT secret
            # For now, decode without verification (development)
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # Skip verification for now
            )
            
            # Supabase stores user ID in 'sub' claim (this is the UUID)
            user_id = decoded.get('sub') or decoded.get('user_id')
            
            if user_id:
                # Validate it's a UUID format
                try:
                    import uuid
                    uuid.UUID(user_id)
                    return user_id
                except (ValueError, AttributeError):
                    print(f"Warning: user_id from token is not a valid UUID: {user_id}")
                    return None
            
            return user_id
        except Exception as e:
            print(f"Error decoding JWT token: {e}")
            return None
    
    # Fallback: try to get from query params or body (for development/testing)
    user_id = request.args.get('user_id') or (request.get_json() or {}).get('user_id')
    
    # Validate it's a UUID if provided
    if user_id:
        try:
            import uuid
            uuid.UUID(user_id)
            return user_id
        except (ValueError, AttributeError):
            print(f"Warning: user_id from request is not a valid UUID: {user_id}")
            return None
    
    return None

