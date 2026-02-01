"""
Task Sync Routes - API endpoints for syncing tasks from class sources
"""

from flask import Blueprint, jsonify, request
import threading
import logging
from services.task_sync_service import sync_tasks_for_class, sync_all_classes_for_user
from db.supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/sync', methods=['POST'])
def sync_tasks():
    """
    Sync tasks for classes.
    
    Request body:
    {
        "user_id": "uuid",           // Required: user to sync for
        "class_id": "uuid",          // Optional: sync specific class only
        "async": true                // Optional: run in background (default: false)
    }
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    class_id = data.get('class_id')
    run_async = data.get('async', False)
    
    logger.info(f"\n🔔 SYNC REQUEST RECEIVED")
    logger.info(f"   user_id: {user_id}")
    logger.info(f"   class_id: {class_id}")
    logger.info(f"   async: {run_async}")
    
    if not user_id:
        logger.error("❌ Missing user_id in request")
        return jsonify({'success': False, 'error': 'user_id is required'}), 400
    
    def do_sync():
        if class_id:
            logger.info(f"🔄 Syncing single class: {class_id}")
            return sync_tasks_for_class(class_id)
        else:
            logger.info(f"🔄 Syncing all classes for user: {user_id}")
            return sync_all_classes_for_user(user_id)
    
    if run_async:
        # Run in background thread
        def background_sync():
            try:
                result = do_sync()
                logger.info(f"✅ Background sync completed: {result}")
            except Exception as e:
                logger.error(f"❌ Background sync error: {e}")
        
        thread = threading.Thread(target=background_sync)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Sync started in background',
            'async': True
        })
    else:
        # Run synchronously
        try:
            result = do_sync()
            logger.info(f"✅ Sync completed: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@tasks_bp.route('/list', methods=['GET'])
def list_tasks():
    """
    Get tasks for a class or user.
    
    Query params:
    - class_id: Filter by class
    - user_id: Get all tasks for user's classes
    - status: Filter by status
    """
    class_id = request.args.get('class_id')
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    try:
        if class_id:
            query = supabase.table('tasks').select('*').eq('class_id', class_id)
        elif user_id:
            # Get tasks for all user's classes
            classes_result = supabase.table('classes').select('id').eq('user_id', user_id).execute()
            class_ids = [c['id'] for c in (classes_result.data or [])]
            
            if not class_ids:
                return jsonify({'success': True, 'tasks': []})
            
            query = supabase.table('tasks').select('*, classes(code, title)').in_('class_id', class_ids)
        else:
            return jsonify({'success': False, 'error': 'class_id or user_id required'}), 400
        
        if status:
            query = query.eq('status', status)
        
        query = query.order('due_at', desc=False, nullsfirst=False)
        result = query.execute()
        
        return jsonify({
            'success': True,
            'tasks': result.data or []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tasks_bp.route('/<task_id>', methods=['PATCH'])
def update_task(task_id: str):
    """
    Update a task (e.g., mark as completed).
    """
    data = request.get_json() or {}
    
    allowed_fields = ['status', 'title', 'due_at', 'task_type']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
    
    try:
        result = supabase.table('tasks').update(update_data).eq('id', task_id).execute()
        
        if result.data:
            return jsonify({
                'success': True,
                'task': result.data[0]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tasks_bp.route('/sources', methods=['GET'])
def list_sources():
    """
    Get class sources for a class or user.
    """
    class_id = request.args.get('class_id')
    user_id = request.args.get('user_id')
    
    try:
        if class_id:
            result = supabase.table('class_sources').select('*').eq('class_id', class_id).execute()
        elif user_id:
            # Get sources for all user's classes
            result = supabase.table('class_sources').select('*, classes(code, title)').execute()
            # Filter to user's classes would need a join, for now return all
        else:
            return jsonify({'success': False, 'error': 'class_id or user_id required'}), 400
        
        return jsonify({
            'success': True,
            'sources': result.data or []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tasks_bp.route('/sources', methods=['POST'])
def add_source():
    """
    Add a new source URL for a class.
    
    Request body:
    {
        "class_id": "uuid",
        "url": "https://...",
        "platform": "prairielearn",  // Optional, will auto-detect
        "label": "CS 225 Assessments"  // Optional
    }
    """
    data = request.get_json() or {}
    class_id = data.get('class_id')
    url = data.get('url')
    
    if not class_id or not url:
        return jsonify({'success': False, 'error': 'class_id and url required'}), 400
    
    # Auto-detect platform if not provided
    platform = data.get('platform')
    if not platform:
        url_lower = url.lower()
        if 'prairielearn' in url_lower:
            platform = 'prairielearn'
        elif 'canvas' in url_lower:
            platform = 'canvas'
        elif 'gradescope' in url_lower:
            platform = 'gradescope'
        elif 'campuswire' in url_lower:
            platform = 'campuswire'
        else:
            platform = 'other'
    
    try:
        result = supabase.table('class_sources').insert({
            'class_id': class_id,
            'url': url,
            'platform': platform,
            'label': data.get('label', '')
        }).execute()
        
        return jsonify({
            'success': True,
            'source': result.data[0] if result.data else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
