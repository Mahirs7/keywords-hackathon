"""
Task Sync Service - Scrapes class sources and syncs tasks to Supabase.

Flow:
1. Read URLs from class_sources table (linked to classes)
2. Scrape each source using appropriate scraper
3. Use LLM to parse raw data into structured tasks
4. Upsert tasks to the tasks table
"""

import os
import json
import requests
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client
from db.supabase_client import supabase

# Import scrapers
try:
    from scrapers.prairielearn_scraper import scrape_prairielearn_assessments
    logger.info("✅ PrairieLearn scraper imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ PrairieLearn scraper not available: {e}")
    scrape_prairielearn_assessments = None

try:
    from scrapers.canvas_scraper import scrape_assignments_for_course_url
    logger.info("✅ Canvas scraper imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Canvas scraper not available: {e}")
    scrape_assignments_for_course_url = None

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def detect_platform(url: str) -> str:
    """Detect which platform a URL belongs to."""
    url_lower = url.lower()
    if 'prairielearn.com' in url_lower or 'prairielearn' in url_lower:
        return 'prairielearn'
    elif 'canvas' in url_lower:
        return 'canvas'
    elif 'gradescope' in url_lower:
        return 'gradescope'
    elif 'campuswire' in url_lower:
        return 'campuswire'
    return 'unknown'


def parse_tasks_with_llm(raw_data: Dict[str, Any], platform: str, class_info: Dict) -> List[Dict]:
    """
    Use GPT-4o to parse raw scraped data into structured task objects.
    
    Args:
        raw_data: Raw scraped data from the scraper
        platform: Platform name (prairielearn, canvas, etc.)
        class_info: Class metadata (id, code, title)
    
    Returns:
        List of task dicts ready for database insertion
    """
    logger.info(f"🤖 Parsing tasks with LLM for {class_info.get('code', 'unknown')} from {platform}")
    logger.info(f"   Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'list'}")
    
    if not OPENAI_API_KEY:
        logger.warning("⚠️ No OpenAI API key - falling back to basic parsing")
        # Fallback: basic parsing without LLM
        return parse_tasks_basic(raw_data, platform, class_info)
    
    system_prompt = """You are a data parser that converts raw scraped course data into structured task objects.

Given raw scraped data from a course platform, extract each assignment/assessment as a task object.

Return a JSON array of task objects with these fields:
- title: string (the assignment/assessment name)
- task_type: string (one of: "assignment", "quiz", "exam", "activity", "homework", "lab", "project")
- due_at: string or null (ISO 8601 datetime if a due date is found, null otherwise)
- url: string or null (link to the assignment if available)
- status: string (one of: "not_started", "in_progress", "completed", "overdue")
- source_label: string (the label/identifier like "A1", "HW2", "Quiz 3")

Parse dates relative to the current year (2026). If only partial date info is given (like "Feb 3"), assume the current year.
Extract status from text like "Not started", "0%", "100%", etc.

Return ONLY valid JSON array, no explanation."""

    user_prompt = f"""Platform: {platform}
Class: {class_info.get('code', '')} - {class_info.get('title', '')}
Current date: {datetime.now().strftime('%Y-%m-%d')}

Raw scraped data:
{json.dumps(raw_data, indent=2)[:8000]}

Extract all tasks as a JSON array:"""

    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 2000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            tasks = json.loads(content.strip())
            logger.info(f"✅ LLM parsed {len(tasks)} tasks")
            
            # Add class_id to each task
            for task in tasks:
                task['class_id'] = class_info['id']
            
            return tasks
        else:
            logger.error(f"❌ LLM API error: {response.status_code} - {response.text}")
            return parse_tasks_basic(raw_data, platform, class_info)
            
    except Exception as e:
        logger.error(f"❌ LLM parsing error: {e}")
        return parse_tasks_basic(raw_data, platform, class_info)


def parse_tasks_basic(raw_data: Dict[str, Any], platform: str, class_info: Dict) -> List[Dict]:
    """
    Basic task parsing without LLM (fallback).
    """
    logger.info(f"📝 Using basic parser for {platform}")
    tasks = []
    
    if platform == 'prairielearn':
        assessments = raw_data.get('assessments', [])
        logger.info(f"   Found {len(assessments)} PrairieLearn assessments")
        for assessment in assessments:
            if not assessment.get('title'):
                continue
            
            task = {
                'class_id': class_info['id'],
                'title': assessment.get('title', 'Untitled'),
                'task_type': 'activity',
                'due_at': None,
                'url': assessment.get('links', [{}])[0].get('href') if assessment.get('links') else None,
                'status': 'not_started' if 'not started' in assessment.get('status', '').lower() else 'in_progress',
                'source_label': assessment.get('label', ''),
            }
            tasks.append(task)
    
    elif platform == 'canvas':
        for assignment in raw_data if isinstance(raw_data, list) else []:
            task = {
                'class_id': class_info['id'],
                'title': assignment.get('title', 'Untitled'),
                'task_type': 'assignment',
                'due_at': assignment.get('due_date'),
                'url': assignment.get('url'),
                'status': 'not_started',
                'source_label': '',
            }
            tasks.append(task)
    
    return tasks


def sync_tasks_for_class(class_id: str) -> Dict[str, Any]:
    """
    Sync tasks for a single class by scraping its sources.
    
    Args:
        class_id: UUID of the class
    
    Returns:
        Dict with sync results
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"🔄 Starting sync for class_id: {class_id}")
    
    # Get class info
    class_result = supabase.table('classes').select('*').eq('id', class_id).single().execute()
    if not class_result.data:
        logger.error(f"❌ Class not found: {class_id}")
        return {'success': False, 'error': 'Class not found'}
    
    class_info = class_result.data
    logger.info(f"📚 Class: {class_info.get('code')} - {class_info.get('title')}")
    
    # Get sources for this class
    sources_result = supabase.table('class_sources').select('*').eq('class_id', class_id).execute()
    sources = sources_result.data or []
    
    logger.info(f"🔗 Found {len(sources)} sources for this class")
    for src in sources:
        src_type = src.get('source_type') or src.get('platform') or 'unknown'
        logger.info(f"   - {src_type}: {src.get('url', 'no url')[:60]}...")
    
    if not sources:
        logger.warning("⚠️ No sources configured for this class")
        return {'success': True, 'message': 'No sources configured', 'tasks_synced': 0}
    
    all_tasks = []
    errors = []
    
    for source in sources:
        url = source.get('url')
        if not url:
            logger.warning(f"⚠️ Source {source.get('id')} has no URL, skipping")
            continue
        
        # Column is 'source_type' not 'platform'
        platform = source.get('source_type') or source.get('platform') or detect_platform(url)
        platform = platform.lower() if platform else 'unknown'
        source_id = source.get('id')
        
        logger.info(f"\n🌐 Scraping {platform}: {url[:80]}...")
        
        try:
            # Scrape based on platform
            raw_data = None
            
            if platform == 'prairielearn':
                if scrape_prairielearn_assessments:
                    logger.info("   Using PrairieLearn scraper...")
                    raw_data = scrape_prairielearn_assessments(url, headless=True)
                else:
                    logger.error("   ❌ PrairieLearn scraper not available!")
                    errors.append(f"PrairieLearn scraper not available")
                    continue
            elif platform == 'canvas':
                if scrape_assignments_for_course_url:
                    logger.info("   Using Canvas scraper...")
                    raw_data = scrape_assignments_for_course_url(url, headless=True)
                else:
                    logger.error("   ❌ Canvas scraper not available!")
                    errors.append(f"Canvas scraper not available")
                    continue
            else:
                logger.warning(f"   ⚠️ No scraper for platform: {platform}")
                errors.append(f"No scraper for platform: {platform}")
                continue
            
            logger.info(f"   📦 Raw data received: {type(raw_data)}")
            if isinstance(raw_data, dict):
                logger.info(f"   📦 Keys: {list(raw_data.keys())}")
                if raw_data.get('assessments'):
                    logger.info(f"   📦 Assessments count: {len(raw_data.get('assessments', []))}")
            
            if raw_data and not raw_data.get('error'):
                # Parse with LLM
                tasks = parse_tasks_with_llm(raw_data, platform, class_info)
                logger.info(f"   ✅ Parsed {len(tasks)} tasks from {platform}")
                
                # Add source metadata
                for task in tasks:
                    task['source_id'] = source_id
                    if not task.get('source_label'):
                        task['source_label'] = platform
                
                all_tasks.extend(tasks)
            elif raw_data and raw_data.get('error'):
                logger.error(f"   ❌ Scraper error: {raw_data.get('error')}")
                errors.append(f"{platform}: {raw_data.get('error')}")
            else:
                logger.warning(f"   ⚠️ No data returned from scraper")
                
        except Exception as e:
            logger.error(f"   ❌ Exception during scraping: {str(e)}")
            errors.append(f"{platform}: {str(e)}")
    
    logger.info(f"\n📊 Total tasks to sync: {len(all_tasks)}")
    
    # Upsert tasks to database
    tasks_synced = 0
    for task in all_tasks:
        try:
            # Prepare task for insert
            task_data = {
                'class_id': task['class_id'],
                'title': task['title'],
                'task_type': task.get('task_type', 'assignment'),
                'due_at': task.get('due_at'),
                'url': task.get('url'),
                'source_id': task.get('source_id'),
                'source_label': task.get('source_label', ''),
                'status': task.get('status', 'not_started'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"   💾 Upserting: {task_data['title'][:50]}...")
            
            # Upsert by class_id + title (to avoid duplicates)
            result = supabase.table('tasks').upsert(
                task_data,
                on_conflict='class_id,title'
            ).execute()
            
            if result.data:
                tasks_synced += 1
                logger.info(f"      ✅ Saved task ID: {result.data[0].get('id', 'unknown')}")
                
        except Exception as e:
            logger.error(f"      ❌ DB insert error: {str(e)}")
            errors.append(f"DB insert error: {str(e)}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"✅ Sync complete: {tasks_synced}/{len(all_tasks)} tasks synced")
    if errors:
        logger.warning(f"⚠️ Errors: {errors}")
    
    return {
        'success': True,
        'tasks_synced': tasks_synced,
        'total_scraped': len(all_tasks),
        'errors': errors if errors else None
    }


def sync_all_classes_for_user(user_id: str) -> Dict[str, Any]:
    """
    Sync tasks for all classes belonging to a user.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        Dict with sync results
    """
    logger.info(f"\n{'#'*60}")
    logger.info(f"🚀 STARTING SYNC ALL CLASSES FOR USER: {user_id}")
    logger.info(f"{'#'*60}\n")
    
    # Get all classes for user
    classes_result = supabase.table('classes').select('id, code, title').eq('user_id', user_id).execute()
    classes = classes_result.data or []
    
    logger.info(f"📚 Found {len(classes)} classes for user")
    for cls in classes:
        logger.info(f"   - {cls.get('code')}: {cls.get('title')}")
    
    if not classes:
        logger.warning("⚠️ No classes found for user")
        return {'success': True, 'message': 'No classes found', 'results': []}
    
    results = []
    total_synced = 0
    
    for cls in classes:
        result = sync_tasks_for_class(cls['id'])
        result['class_code'] = cls.get('code')
        result['class_title'] = cls.get('title')
        results.append(result)
        
        if result.get('success'):
            total_synced += result.get('tasks_synced', 0)
    
    logger.info(f"\n{'#'*60}")
    logger.info(f"🎉 SYNC COMPLETE: {total_synced} total tasks synced across {len(classes)} classes")
    logger.info(f"{'#'*60}\n")
    
    return {
        'success': True,
        'total_tasks_synced': total_synced,
        'classes_processed': len(classes),
        'results': results
    }
