"""Seed sample tasks for testing"""
from db.supabase_client import supabase
from datetime import datetime, timedelta
import random

# Get all classes
classes = supabase.table('classes').select('id, code, title').execute()
print(f"Found {len(classes.data or [])} classes")

tasks_to_insert = []
now = datetime.now()

for cls in (classes.data or []):
    class_id = cls['id']
    code = cls.get('code', 'CS')
    
    # Generate realistic tasks for each class
    task_templates = [
        {'title': f'{code} Homework 1', 'task_type': 'homework', 'days': 3},
        {'title': f'{code} Homework 2', 'task_type': 'homework', 'days': 10},
        {'title': f'{code} Quiz 1', 'task_type': 'quiz', 'days': 5},
        {'title': f'{code} MP1: Getting Started', 'task_type': 'assignment', 'days': 7},
        {'title': f'{code} Lab 1', 'task_type': 'lab', 'days': 2},
        {'title': f'{code} Lab 2', 'task_type': 'lab', 'days': 9},
        {'title': f'{code} Midterm 1', 'task_type': 'exam', 'days': 14},
        {'title': f'{code} Reading: Chapter 1-3', 'task_type': 'reading', 'days': 4},
    ]
    
    for t in task_templates:
        due = now + timedelta(days=t['days'], hours=random.randint(10, 23))
        tasks_to_insert.append({
            'class_id': class_id,
            'title': t['title'],
            'task_type': t['task_type'],
            'due_at': due.isoformat(),
            'status': random.choice(['not_started', 'not_started', 'in_progress']),
            'source_label': 'Canvas' if 'Homework' in t['title'] or 'MP' in t['title'] else 'PrairieLearn',
        })

print(f"Inserting {len(tasks_to_insert)} tasks...")

# Clear existing tasks first
supabase.table('tasks').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared existing tasks")

# Insert all tasks
for task in tasks_to_insert:
    try:
        supabase.table('tasks').insert(task).execute()
        print(f"  ✓ {task['title']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Verify
result = supabase.table('tasks').select('id').execute()
print(f"\nTotal tasks now: {len(result.data or [])}")
