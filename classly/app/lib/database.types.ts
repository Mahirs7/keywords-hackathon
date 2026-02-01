// Database types matching Supabase schema
// These replace the mock data types

export interface Profile {
  id: string;
  name: string | null;
  email: string | null;
  avatar_url: string | null;
  university: string;
  preferences: Record<string, unknown>;
  msft_email: string | null;
  msft_password: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserPlatform {
  id: string;
  user_id: string;
  platform: 'canvas' | 'gradescope' | 'campuswire' | 'prairielearn';
  connected: boolean;
  last_synced: string | null;
  sync_status: 'never' | 'syncing' | 'success' | 'failed';
  error_message: string | null;
  created_at: string;
}

export interface Course {
  id: string;
  user_id: string;
  platform: string;
  platform_course_id: string | null;
  name: string;
  department: string | null;
  course_number: string | null;
  section: string | null;
  crn: string | null;
  schedule: {
    days?: string[];
    time?: string;
    location?: string;
  } | null;
  instructor: string | null;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Deadline {
  id: string;
  user_id: string;
  course_id: string | null;
  platform: 'canvas' | 'gradescope' | 'campuswire' | 'prairielearn';
  platform_assignment_id: string | null;
  title: string;
  course_name: string | null;
  type: string;
  due_date: string | null;
  due_date_text: string | null;
  status: 'pending' | 'submitted' | 'graded' | 'late' | 'missing';
  points_possible: number | null;
  points_earned: number | null;
  url: string | null;
  instructions_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduleItem {
  id: string;
  user_id: string;
  course_id: string | null;
  title: string;
  type: 'class' | 'study' | 'break' | 'office_hours' | 'exam' | 'other';
  start_time: string | null;
  end_time: string | null;
  duration_minutes: number | null;
  location: string | null;
  color: string;
  recurring: boolean;
  days: string[] | null;
  specific_date: string | null;
  related_deadline_id: string | null;
  created_at: string;
}

export interface ScrapeJob {
  id: string;
  user_id: string;
  platform: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string | null;
  completed_at: string | null;
  items_synced: number;
  error_message: string | null;
  created_at: string;
}

// Platform summary for dashboard cards
export interface PlatformSummary {
  platform: 'canvas' | 'gradescope' | 'campuswire' | 'prairielearn';
  name: string;
  pending_count: number;
  connected: boolean;
  last_synced: string | null;
  color: string;
  label: string;
}

// Helper to format platform names
export const platformNames: Record<string, string> = {
  canvas: 'Canvas',
  gradescope: 'Gradescope',
  campuswire: 'Campuswire',
  prairielearn: 'PrairieLearn',
};

export const platformColors: Record<string, string> = {
  canvas: '#e74c3c',
  gradescope: '#27ae60',
  campuswire: '#3498db',
  prairielearn: '#9b59b6',
};
