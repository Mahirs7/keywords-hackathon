"""
Scrape routes - Trigger and manage scraping jobs
"""

from flask import Blueprint, jsonify, request
from db.supabase_client import supabase
from services.scraper_service import ScraperService
import threading

scrape_bp = Blueprint('scrape', __name__)


@scrape_bp.route('/start', methods=['POST'])
def start_scrape():
    """
    Start scraping for specified platforms.
    Called by the Next.js API route after creating scrape jobs.
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    platforms = data.get('platforms', [])
    job_ids = data.get('job_ids', [])

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    if not platforms:
        platforms = ['canvas', 'gradescope', 'campuswire', 'prairielearn']

    # Run scraping in background thread
    def run_scrape():
        scraper = ScraperService(user_id)
        for i, platform in enumerate(platforms):
            job_id = job_ids[i] if i < len(job_ids) else None
            try:
                scraper.scrape_platform(platform, job_id)
            except Exception as e:
                print(f"Error scraping {platform}: {e}")
                if job_id:
                    supabase.table('scrape_jobs').update({
                        'status': 'failed',
                        'error_message': str(e)
                    }).eq('id', job_id).execute()

    thread = threading.Thread(target=run_scrape)
    thread.start()

    return jsonify({
        "message": "Scraping started",
        "platforms": platforms
    })


@scrape_bp.route('/status', methods=['GET'])
def get_scrape_status():
    """Get status of recent scrape jobs for the user"""
    # Get user from auth header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(' ')[1]
    
    # Verify token and get user
    try:
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 401

    # Get recent jobs
    result = supabase.table('scrape_jobs') \
        .select('*') \
        .eq('user_id', user_id) \
        .order('created_at', desc=True) \
        .limit(10) \
        .execute()

    return jsonify({"jobs": result.data})


@scrape_bp.route('/sync-from-courses', methods=['POST'])
def sync_from_courses():
    """
    Get the current user's classes and their LMS links from Supabase (classes + class_sources),
    run the appropriate scraper per source (Canvas, PrairieLearn, etc.), and save
    assignments to the tasks table.
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    job_id = None
    try:
        job_res = supabase.table('scrape_jobs').insert({
            'user_id': user_id,
            'platform': 'canvas',
            'status': 'pending',
        }).select().single().execute()
        job_id = job_res.data['id'] if job_res.data else None
    except Exception:
        pass

    def run_sync():
        scraper = ScraperService(user_id)
        try:
            scraper.sync_from_user_courses(job_id=job_id)
        except Exception as e:
            print(f"Sync from courses failed: {e}")
            if job_id:
                supabase.table('scrape_jobs').update({
                    'status': 'failed',
                    'error_message': str(e)
                }).eq('id', job_id).execute()

    thread = threading.Thread(target=run_sync)
    thread.start()

    return jsonify({
        "message": "Sync from courses started",
        "job_id": job_id,
    })


@scrape_bp.route('/cancel/<job_id>', methods=['POST'])
def cancel_scrape(job_id):
    """Cancel a running scrape job"""
    # Update job status to cancelled
    result = supabase.table('scrape_jobs') \
        .update({'status': 'failed', 'error_message': 'Cancelled by user'}) \
        .eq('id', job_id) \
        .eq('status', 'running') \
        .execute()

    if result.data:
        return jsonify({"message": "Job cancelled"})
    else:
        return jsonify({"error": "Job not found or already completed"}), 404
