"""
Scraper Service - Orchestrates scraping from all platforms and stores to Supabase
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Add parent directories to path for importing scrapers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from db.supabase_client import supabase

try:
    from scrapers.canvas_scraper import scrape_assignments_for_course_url as canvas_scrape_url
except ImportError:
    canvas_scrape_url = None


class ScraperService:
    """Service to orchestrate scraping and data storage"""

    def __init__(self, user_id: str):
        self.user_id = user_id

    def scrape_platform(self, platform: str, job_id: Optional[str] = None):
        """
        Scrape a single platform and store results
        """
        if job_id:
            # Update job status to running
            supabase.table('scrape_jobs').update({
                'status': 'running',
                'started_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', job_id).execute()

        try:
            items_synced = 0

            if platform == 'canvas':
                items_synced = self._scrape_canvas()
            elif platform == 'gradescope':
                items_synced = self._scrape_gradescope()
            elif platform == 'campuswire':
                items_synced = self._scrape_campuswire()
            elif platform == 'prairielearn':
                items_synced = self._scrape_prairielearn()
            else:
                raise ValueError(f"Unknown platform: {platform}")

            if job_id:
                supabase.table('scrape_jobs').update({
                    'status': 'completed',
                    'completed_at': datetime.now(timezone.utc).isoformat(),
                    'items_synced': items_synced
                }).eq('id', job_id).execute()

            # Update user_platforms last_synced
            supabase.table('user_platforms').upsert({
                'user_id': self.user_id,
                'platform': platform,
                'connected': True,
                'last_synced': datetime.now(timezone.utc).isoformat(),
                'sync_status': 'success'
            }, on_conflict='user_id,platform').execute()

            return items_synced

        except Exception as e:
            if job_id:
                supabase.table('scrape_jobs').update({
                    'status': 'failed',
                    'error_message': str(e)
                }).eq('id', job_id).execute()

            supabase.table('user_platforms').upsert({
                'user_id': self.user_id,
                'platform': platform,
                'sync_status': 'failed',
                'error_message': str(e)
            }, on_conflict='user_id,platform').execute()

            raise

    def _scrape_canvas(self) -> int:
        """
        Scrape Canvas and store assignments.
        For now, loads from existing JSON file if available.
        """
        # Try to load from existing scraped file
        canvas_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                                    'canvas-scraper', 'canvas_snapshot.json')
        
        if os.path.exists(canvas_file):
            with open(canvas_file, 'r') as f:
                data = json.load(f)
            return self._process_canvas_data(data)
        
        # TODO: Implement live scraping with Selenium
        # This requires handling browser automation in a server context
        print("Canvas scraper: No existing data file found")
        return 0

    def _process_canvas_data(self, data: Dict[str, Any]) -> int:
        """Process Canvas JSON data and store to Supabase"""
        items_synced = 0

        for course_data in data.get('courses', []):
            # Upsert course
            course_result = supabase.table('courses').upsert({
                'user_id': self.user_id,
                'platform': 'canvas',
                'platform_course_id': str(course_data['id']),
                'name': course_data['name'],
                'color': '#e74c3c'  # Canvas red
            }, on_conflict='user_id,platform,platform_course_id').execute()

            course_id = course_result.data[0]['id'] if course_result.data else None

            # Process assignments
            for assignment in course_data.get('assignments', []):
                detail = assignment.get('detail', {})
                
                # Parse due date
                due_date = None
                if detail.get('due_at_iso'):
                    due_date = detail['due_at_iso']

                supabase.table('deadlines').upsert({
                    'user_id': self.user_id,
                    'course_id': course_id,
                    'platform': 'canvas',
                    'platform_assignment_id': str(assignment['id']),
                    'title': assignment['title'],
                    'course_name': course_data['name'],
                    'type': 'assignment',
                    'due_date': due_date,
                    'due_date_text': detail.get('due_at_text') or assignment.get('due_text_raw'),
                    'status': 'pending',
                    'points_possible': detail.get('points_possible'),
                    'url': assignment.get('url'),
                    'instructions_text': detail.get('instructions_text')
                }, on_conflict='user_id,platform,platform_assignment_id').execute()

                items_synced += 1

        return items_synced

    def _scrape_gradescope(self) -> int:
        """Scrape Gradescope submissions"""
        # TODO: Implement Gradescope scraper
        print("Gradescope scraper: Not yet implemented")
        return 0

    def _scrape_campuswire(self) -> int:
        """Scrape Campuswire posts"""
        campuswire_file = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                        'campuswire_posts.json')
        
        if os.path.exists(campuswire_file):
            with open(campuswire_file, 'r') as f:
                data = json.load(f)
            return self._process_campuswire_data(data)
        
        print("Campuswire scraper: No existing data file found")
        return 0

    def _process_campuswire_data(self, data: Dict[str, Any]) -> int:
        """Process Campuswire JSON data"""
        # Campuswire posts don't directly map to deadlines
        # Could be used for discussion tracking
        return len(data.get('posts', []))

    def _scrape_prairielearn(self) -> int:
        """Scrape PrairieLearn assessments"""
        pl_file = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                               'prairielearn_assessments.json')
        
        if os.path.exists(pl_file):
            with open(pl_file, 'r') as f:
                data = json.load(f)
            return self._process_prairielearn_data(data)
        
        print("PrairieLearn scraper: No existing data file found")
        return 0

    def _process_prairielearn_data(self, data: Dict[str, Any]) -> int:
        """Process PrairieLearn JSON data"""
        items_synced = 0

        for course_data in data.get('courses', []):
            # Upsert course
            course_result = supabase.table('courses').upsert({
                'user_id': self.user_id,
                'platform': 'prairielearn',
                'platform_course_id': course_data.get('course_id', course_data.get('name')),
                'name': course_data['name'],
                'color': '#9b59b6'  # PrairieLearn purple
            }, on_conflict='user_id,platform,platform_course_id').execute()

            course_id = course_result.data[0]['id'] if course_result.data else None

            # Process assessments
            for assessment in course_data.get('assessments', []):
                supabase.table('deadlines').upsert({
                    'user_id': self.user_id,
                    'course_id': course_id,
                    'platform': 'prairielearn',
                    'platform_assignment_id': assessment.get('id', assessment.get('name')),
                    'title': assessment['name'],
                    'course_name': course_data['name'],
                    'type': assessment.get('type', 'quiz'),
                    'due_date': assessment.get('due_date'),
                    'due_date_text': assessment.get('due_date_text'),
                    'status': 'pending',
                    'url': assessment.get('url')
                }, on_conflict='user_id,platform,platform_assignment_id').execute()

                items_synced += 1

        return items_synced

    def sync_from_user_courses(self, job_id: Optional[str] = None) -> int:
        """
        Get the user's classes and their LMS links from Supabase (classes + class_sources),
        run the appropriate scraper per source (Canvas, etc.), and save assignments
        to the tasks table. Schema: users -> classes -> class_sources -> tasks.
        """
        if job_id:
            try:
                supabase.table('scrape_jobs').update({
                    'status': 'running',
                    'started_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', job_id).execute()
            except Exception:
                pass

        try:
            # 1. Get user's classes (id, title, code)
            classes_res = supabase.table('classes').select('id, title, code').eq('user_id', self.user_id).execute()
            if not classes_res.data:
                return 0
            class_ids = [c['id'] for c in classes_res.data]

            # 2. Get class_sources (id, class_id, source_type, url) for those classes
            sources_res = supabase.table('class_sources').select('id, class_id, source_type, url').in_('class_id', class_ids).execute()
            if not sources_res.data:
                return 0

            profile_dir = os.environ.get('CANVAS_PROFILE_DIR')
            items_synced = 0
            now_iso = datetime.now(timezone.utc).isoformat()

            for row in sources_res.data:
                source_type = (row.get('source_type') or '').strip().lower()
                url = (row.get('url') or '').strip()
                class_id = row.get('class_id')
                source_row_id = row.get('id')

                if not url or not class_id:
                    continue

                if source_type == 'canvas':
                    if not canvas_scrape_url:
                        continue
                    assignments = canvas_scrape_url(course_url=url, headless=True, profile_dir=profile_dir)
                    for a in assignments:
                        supabase.table('tasks').insert({
                            'class_id': class_id,
                            'title': a['title'],
                            'task_type': 'assignment',
                            'due_at': None,
                            'url': a.get('url'),
                            'source_id': str(a['id']),
                            'source_label': 'Canvas Assignment',
                            'status': 'todo',
                        }).execute()
                        items_synced += 1
                    try:
                        supabase.table('class_sources').update({
                            'last_fetched_at': now_iso,
                            'status': 'active',
                        }).eq('id', source_row_id).execute()
                    except Exception:
                        pass
                # Add more source_type handlers (prairielearn, moodle, etc.) here

            if job_id:
                try:
                    supabase.table('scrape_jobs').update({
                        'status': 'completed',
                        'completed_at': now_iso,
                        'items_synced': items_synced
                    }).eq('id', job_id).execute()
                except Exception:
                    pass

            return items_synced
        except Exception as e:
            if job_id:
                try:
                    supabase.table('scrape_jobs').update({
                        'status': 'failed',
                        'error_message': str(e)
                    }).eq('id', job_id).execute()
                except Exception:
                    pass
            raise


def load_scraped_data_for_user(user_id: str, platforms: Optional[List[str]] = None):
    """
    Convenience function to load all scraped data for a user.
    Called on user sign-in to populate initial data.
    """
    service = ScraperService(user_id)
    
    if platforms is None:
        platforms = ['canvas', 'prairielearn', 'campuswire']

    results = {}
    for platform in platforms:
        try:
            count = service.scrape_platform(platform)
            results[platform] = {'status': 'success', 'items': count}
        except Exception as e:
            results[platform] = {'status': 'error', 'error': str(e)}

    return results
