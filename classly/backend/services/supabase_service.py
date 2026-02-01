"""
Supabase Service
Handles database operations for assignments
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            self.client = None
            print("Warning: Supabase credentials not configured. Using mock data.")
        else:
            try:
                self.client: Optional[Client] = create_client(supabase_url, supabase_key)
            except Exception as e:
                print(f"Warning: Error initializing Supabase client: {e}")
                print("Falling back to mock data mode.")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self.client is not None
    
    def get_assignments(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch assignments from Supabase
        
        Args:
            week_start: Start of week (defaults to start of current week)
            week_end: End of week (defaults to end of current week)
            
        Returns:
            List of assignment dictionaries
        """
        if not self.is_configured():
            # Return mock data if Supabase not configured
            return self._get_mock_assignments(week_start, week_end)
        
        try:
            query = self.client.table('assignments').select('title, due_at, url')
            
            if week_start:
                query = query.gte('due_at', week_start.isoformat())
            if week_end:
                query = query.lte('due_at', week_end.isoformat())
            
            response = query.order('due_at').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching assignments from Supabase: {e}")
            return self._get_mock_assignments(week_start, week_end)
    
    def get_pending_assignments(self) -> List[Dict[str, Any]]:
        """
        Get all pending assignments (not submitted)
        
        Returns:
            List of pending assignment dictionaries
        """
        if not self.is_configured():
            return self._get_mock_assignments()
        
        try:
            response = self.client.table('assignments')\
                .select('title, due_at, url')\
                .order('due_at')\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching pending assignments: {e}")
            return self._get_mock_assignments()
    
    def _get_mock_assignments(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Return mock assignments for development"""
        now = datetime.now()
        if not week_start:
            week_start = now - timedelta(days=now.weekday())
        if not week_end:
            week_end = week_start + timedelta(days=7)
        
        mock_assignments = [
            {
                'title': 'Problem Set 4: Dynamic Programming',
                'due_at': (now + timedelta(days=3)).isoformat(),
                'url': 'https://canvas.illinois.edu/courses/123/assignments/456'
            },
            {
                'title': 'Lab 5: Binary Search Trees',
                'due_at': (now + timedelta(days=4)).isoformat(),
                'url': 'https://gradescope.com/courses/789/assignments/101'
            },
            {
                'title': 'Homework 6: Integration',
                'due_at': (now + timedelta(days=5)).isoformat(),
                'url': 'https://canvas.illinois.edu/courses/456/assignments/789'
            }
        ]
        
        # Filter by date range if provided
        filtered = []
        for assignment in mock_assignments:
            due_at = datetime.fromisoformat(assignment['due_at'])
            if week_start and due_at < week_start:
                continue
            if week_end and due_at > week_end:
                continue
            filtered.append(assignment)
        
        return filtered

# Singleton instance
supabase_service = SupabaseService()

