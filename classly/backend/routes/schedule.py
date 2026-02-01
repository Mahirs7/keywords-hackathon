"""
Schedule API Routes
Manages daily schedule including classes and study blocks
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

schedule_bp = Blueprint('schedule', __name__)

# Mock data - will be replaced with real Supabase calls
MOCK_SCHEDULE = [
    {
        "id": "1",
        "title": "CS 101 Lecture",
        "type": "class",
        "start_time": "09:00",
        "end_time": "10:15",
        "duration": "1h 15m",
        "location": "Siebel 1404",
        "color": "#3b82f6",
        "recurring": True,
        "days": ["Monday", "Wednesday", "Friday"]
    },
    {
        "id": "2",
        "title": "Study: Dynamic Programming",
        "type": "study",
        "start_time": "10:30",
        "end_time": "12:30",
        "duration": "2h",
        "location": None,
        "color": "#8b5cf6",
        "recurring": False,
        "related_deadline_id": "1"
    },
    {
        "id": "3",
        "title": "Lunch Break",
        "type": "break",
        "start_time": "12:30",
        "end_time": "13:30",
        "duration": "1h",
        "location": None,
        "color": "#6b7280",
        "recurring": True,
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    {
        "id": "4",
        "title": "MATH 201 Lecture",
        "type": "class",
        "start_time": "14:00",
        "end_time": "15:00",
        "duration": "1h",
        "location": "Altgeld 314",
        "color": "#10b981",
        "recurring": True,
        "days": ["Tuesday", "Thursday"]
    },
    {
        "id": "5",
        "title": "Work on CS Lab 5",
        "type": "study",
        "start_time": "15:30",
        "end_time": "17:30",
        "duration": "2h",
        "location": "Grainger Library",
        "color": "#f59e0b",
        "recurring": False,
        "related_deadline_id": "2"
    },
    {
        "id": "6",
        "title": "Office Hours - CS 444",
        "type": "office_hours",
        "start_time": "16:00",
        "end_time": "17:00",
        "duration": "1h",
        "location": "Siebel 2124",
        "color": "#ec4899",
        "recurring": True,
        "days": ["Wednesday"]
    }
]


@schedule_bp.route('/', methods=['GET'])
def get_schedule():
    """Get full schedule"""
    return jsonify({
        "success": True,
        "data": MOCK_SCHEDULE,
        "count": len(MOCK_SCHEDULE)
    })


@schedule_bp.route('/today', methods=['GET'])
def get_today_schedule():
    """Get today's schedule"""
    today = datetime.now().strftime("%A")
    
    # Filter to today's events (recurring or one-time)
    schedule = [
        event for event in MOCK_SCHEDULE
        if not event.get('recurring') or today in event.get('days', [])
    ]
    
    # Sort by start time
    schedule.sort(key=lambda x: x['start_time'])
    
    return jsonify({
        "success": True,
        "data": schedule,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "day": today,
        "count": len(schedule)
    })


@schedule_bp.route('/week', methods=['GET'])
def get_week_schedule():
    """Get this week's schedule"""
    # In production, this would calculate the actual week
    return jsonify({
        "success": True,
        "data": MOCK_SCHEDULE,
        "week_start": datetime.now().strftime("%Y-%m-%d"),
        "count": len(MOCK_SCHEDULE)
    })


@schedule_bp.route('/', methods=['POST'])
def add_schedule_item():
    """Add a new schedule item"""
    data = request.get_json()
    
    # Validate required fields
    required = ['title', 'type', 'start_time', 'end_time']
    if not all(field in data for field in required):
        return jsonify({
            "success": False, 
            "error": "Missing required fields"
        }), 400
    
    # Create new item (mock - would save to Supabase)
    new_item = {
        "id": str(len(MOCK_SCHEDULE) + 1),
        **data
    }
    
    return jsonify({
        "success": True,
        "data": new_item,
        "message": "Schedule item created"
    }), 201


@schedule_bp.route('/<item_id>', methods=['DELETE'])
def delete_schedule_item(item_id):
    """Delete a schedule item"""
    item = next((s for s in MOCK_SCHEDULE if s['id'] == item_id), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404
    
    return jsonify({
        "success": True,
        "message": "Schedule item deleted"
    })
