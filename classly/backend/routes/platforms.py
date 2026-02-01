"""
Platforms API Routes
Per-platform data and summaries for Canvas, Gradescope, PrairieLearn, Campuswire
"""

from flask import Blueprint, jsonify, request

platforms_bp = Blueprint('platforms', __name__)

# Mock platform summaries
MOCK_PLATFORM_SUMMARIES = {
    "canvas": {
        "id": "canvas",
        "name": "Canvas",
        "icon": "book",
        "color": "#e74c3c",
        "connected": True,
        "last_synced": "2026-01-31T15:30:00Z",
        "stats": {
            "pending_tasks": 4,
            "upcoming_deadlines": 3,
            "unread_announcements": 2
        },
        "courses": [
            {"id": "1", "name": "CS 101 - Intro to Computer Science", "pending": 2},
            {"id": "2", "name": "MATH 201 - Calculus II", "pending": 1},
            {"id": "3", "name": "PSYC 100 - Intro to Psychology", "pending": 1}
        ]
    },
    "gradescope": {
        "id": "gradescope",
        "name": "Gradescope",
        "icon": "clipboard-check",
        "color": "#27ae60",
        "connected": True,
        "last_synced": "2026-01-31T15:30:00Z",
        "stats": {
            "submissions_due": 2,
            "graded_assignments": 5,
            "pending_regrade": 0
        },
        "courses": [
            {"id": "1", "name": "CS 101", "submissions_due": 1},
            {"id": "2", "name": "CS 444", "submissions_due": 1}
        ]
    },
    "campuswire": {
        "id": "campuswire",
        "name": "Campuswire",
        "icon": "message-circle",
        "color": "#3498db",
        "connected": True,
        "last_synced": "2026-01-31T15:30:00Z",
        "stats": {
            "new_posts": 8,
            "unread_replies": 3,
            "unanswered_questions": 2
        },
        "courses": [
            {"id": "GCE159BBC", "name": "CS 444 - Deep Learning", "new_posts": 8}
        ]
    },
    "prairielearn": {
        "id": "prairielearn",
        "name": "PrairieLearn",
        "icon": "code",
        "color": "#9b59b6",
        "connected": True,
        "last_synced": "2026-01-31T15:30:00Z",
        "stats": {
            "active_assessments": 2,
            "completed_today": 1,
            "average_score": 87
        },
        "courses": [
            {"id": "206336", "name": "CS 444 - Deep Learning", "active": 2}
        ]
    }
}

# Mock detailed platform data
MOCK_CANVAS_DATA = {
    "announcements": [
        {
            "id": "1",
            "title": "Midterm Exam Details",
            "course": "CS 101",
            "posted_at": "2026-01-30T10:00:00Z",
            "read": False
        },
        {
            "id": "2", 
            "title": "Office Hours Change",
            "course": "MATH 201",
            "posted_at": "2026-01-29T14:00:00Z",
            "read": True
        }
    ],
    "assignments": [
        {
            "id": "1",
            "title": "Problem Set 4: Dynamic Programming",
            "course": "CS 101",
            "due_date": "2026-02-04T23:59:00Z",
            "points": 100,
            "submitted": False
        }
    ],
    "grades": [
        {
            "course": "CS 101",
            "current_grade": "A-",
            "current_score": 91.5
        },
        {
            "course": "MATH 201", 
            "current_grade": "B+",
            "current_score": 87.2
        }
    ]
}

MOCK_CAMPUSWIRE_DATA = {
    "posts": [
        {
            "id": "14",
            "title": "CS 444 Canvas Question",
            "preview": "Hi, I just wanted to check if it's norm...",
            "author": "Anonymous",
            "category": "Lecture questions",
            "posted_at": "2026-01-30T12:00:00Z",
            "comments": 0,
            "resolved": False
        },
        {
            "id": "12",
            "title": "Difficulty expectation for mp",
            "preview": "How much of time commitment and...",
            "author": "Student",
            "category": "Logistics",
            "posted_at": "2026-01-29T10:00:00Z",
            "comments": 3,
            "resolved": True
        },
        {
            "id": "7",
            "title": "Google Colab Pro Setup",
            "preview": "I recall Professor Svetlana mentioning...",
            "author": "Zuhair Ghias",
            "category": "Lecture questions",
            "posted_at": "2026-01-25T09:00:00Z",
            "comments": 6,
            "resolved": True,
            "pinned": True
        }
    ]
}


@platforms_bp.route('/', methods=['GET'])
def get_all_platforms():
    """Get summary of all connected platforms"""
    return jsonify({
        "success": True,
        "data": list(MOCK_PLATFORM_SUMMARIES.values()),
        "count": len(MOCK_PLATFORM_SUMMARIES)
    })


@platforms_bp.route('/summary', methods=['GET'])
def get_platform_summary():
    """Get quick stats for dashboard cards"""
    summary = {
        "canvas": {
            "count": MOCK_PLATFORM_SUMMARIES["canvas"]["stats"]["pending_tasks"],
            "label": "pending tasks"
        },
        "gradescope": {
            "count": MOCK_PLATFORM_SUMMARIES["gradescope"]["stats"]["submissions_due"],
            "label": "submissions due"
        },
        "campuswire": {
            "count": MOCK_PLATFORM_SUMMARIES["campuswire"]["stats"]["new_posts"],
            "label": "new posts"
        },
        "prairielearn": {
            "count": MOCK_PLATFORM_SUMMARIES["prairielearn"]["stats"]["active_assessments"],
            "label": "active assessments"
        }
    }
    
    return jsonify({
        "success": True,
        "data": summary
    })


@platforms_bp.route('/<platform_id>', methods=['GET'])
def get_platform(platform_id):
    """Get detailed data for a specific platform"""
    platform = MOCK_PLATFORM_SUMMARIES.get(platform_id)
    
    if not platform:
        return jsonify({"success": False, "error": "Platform not found"}), 404
    
    # Add detailed data based on platform
    detailed_data = platform.copy()
    
    if platform_id == "canvas":
        detailed_data["details"] = MOCK_CANVAS_DATA
    elif platform_id == "campuswire":
        detailed_data["details"] = MOCK_CAMPUSWIRE_DATA
    
    return jsonify({
        "success": True,
        "data": detailed_data
    })


@platforms_bp.route('/<platform_id>/sync', methods=['POST'])
def sync_platform(platform_id):
    """Trigger a sync for a specific platform"""
    platform = MOCK_PLATFORM_SUMMARIES.get(platform_id)
    
    if not platform:
        return jsonify({"success": False, "error": "Platform not found"}), 404
    
    # In production, this would trigger the actual scraper
    return jsonify({
        "success": True,
        "message": f"Sync started for {platform['name']}",
        "platform_id": platform_id
    })


@platforms_bp.route('/connect', methods=['POST'])
def connect_platform():
    """Connect a new platform"""
    data = request.get_json()
    platform_id = data.get('platform_id')
    
    if not platform_id:
        return jsonify({"success": False, "error": "Platform ID required"}), 400
    
    # In production, this would initiate OAuth or credential storage
    return jsonify({
        "success": True,
        "message": f"Platform {platform_id} connection initiated",
        "next_step": "authenticate"
    })
