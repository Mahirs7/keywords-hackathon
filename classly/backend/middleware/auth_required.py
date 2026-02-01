from functools import wraps
from flask import request, jsonify
from db.supabase_client import supabase

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "error": "Missing Authorization header"
            }), 401

        token = auth_header.replace("Bearer ", "")

        try:
            user = supabase.auth.get_user(token).user
        except Exception:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token!"
            }), 401

        request.user = user

        return f(*args, **kwargs)

    return decorated
