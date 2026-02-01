"""
Deadlines API Routes
Aggregates assignment deadlines from all platforms
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

deadlines_bp = Blueprint('deadlines', __name__)

# Mock data - will be replaced with real Supabase/scraper calls
MOCK_DEADLINES = [
    {
        "id": "1",
        "title": "Problem Set 4: Dynamic Programming",
        "course": "CS 101 - Intro to Computer Science",
        "platform": "canvas",
        "type": "assignment",
        "due_date": "2026-02-04T23:59:00Z",
        "due_time": "11:59 PM",
        "status": "pending",
        "url": "https://canvas.illinois.edu/courses/123/assignments/456"
    },
    {
        "id": "2",
        "title": "Lab 5: Binary Search Trees",
        "course": "CS 101 - Intro to Computer Science",
        "platform": "gradescope",
        "type": "coding",
        "due_date": "2026-02-05T23:59:00Z",
        "due_time": "11:59 PM",
        "status": "pending",
        "url": "https://gradescope.com/courses/123/assignments/789"
    },
    {
        "id": "3",
        "title": "Homework 6: Integration",
        "course": "MATH 201 - Calculus II",
        "platform": "canvas",
        "type": "homework",
        "due_date": "2026-02-06T23:59:00Z",
        "due_time": "11:59 PM",
        "status": "pending",
        "url": "https://canvas.illinois.edu/courses/456/assignments/789"
    },
    {
        "id": "4",
        "title": "Discussion: Research Methods",
        "course": "PSYC 100 - Intro to Psychology",
        "platform": "campuswire",
        "type": "discussion",
        "due_date": "2026-02-07T17:00:00Z",
        "due_time": "5:00 PM",
        "status": "pending",
        "url": "https://campuswire.com/c/ABC123/feed/post/456"
    },
    {
        "id": "5",
        "title": "Quiz 3: Machine Learning Basics",
        "course": "CS 444 - Deep Learning",
        "platform": "prairielearn",
        "type": "quiz",
        "due_date": "2026-02-08T23:59:00Z",
        "due_time": "11:59 PM",
        "status": "pending",
        "url": "https://us.prairielearn.com/pl/course_instance/206336"
    }
]


@deadlines_bp.route('/', methods=['GET'])
def get_all_deadlines():
    """Get all upcoming deadlines across platforms"""
    platform = request.args.get('platform')
    limit = request.args.get('limit', type=int)
    
    deadlines = MOCK_DEADLINES.copy()
    
    # Filter by platform if specified
    if platform:
        deadlines = [d for d in deadlines if d['platform'] == platform]
    
    # Sort by due date
    deadlines.sort(key=lambda x: x['due_date'])
    
    # Limit results
    if limit:
        deadlines = deadlines[:limit]
    
    return jsonify({
        "success": True,
        "data": deadlines,
        "count": len(deadlines)
    })


@deadlines_bp.route('/upcoming', methods=['GET'])
def get_upcoming_deadlines():
    """Get deadlines for the next 7 days"""
    days = request.args.get('days', default=7, type=int)
    
    # Filter to upcoming deadlines
    deadlines = [d for d in MOCK_DEADLINES if d['status'] == 'pending']
    deadlines.sort(key=lambda x: x['due_date'])
    
    return jsonify({
        "success": True,
        "data": deadlines,
        "count": len(deadlines)
    })


@deadlines_bp.route('/today', methods=['GET'])
def get_today_deadlines():
    """Get deadlines due today"""
    today = datetime.now().date()
    
    deadlines = [
        d for d in MOCK_DEADLINES 
        if datetime.fromisoformat(d['due_date'].replace('Z', '+00:00')).date() == today
    ]
    
    return jsonify({
        "success": True,
        "data": deadlines,
        "count": len(deadlines)
    })


@deadlines_bp.route('/<deadline_id>', methods=['GET'])
def get_deadline(deadline_id):
    """Get a specific deadline by ID"""
    deadline = next((d for d in MOCK_DEADLINES if d['id'] == deadline_id), None)
    
    if not deadline:
        return jsonify({"success": False, "error": "Deadline not found"}), 404
    
    return jsonify({
        "success": True,
        "data": deadline
    })
