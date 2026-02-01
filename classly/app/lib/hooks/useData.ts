'use client';

import { createClient } from '@/app/lib/supabase/client';
import { useState, useEffect, useCallback } from 'react';
import type { 
  Profile, 
  Deadline, 
  ScheduleItem, 
  PlatformSummary,
  Course,
  UserPlatform 
} from '@/app/lib/database.types';
import { platformNames, platformColors } from '@/app/lib/database.types';

// ============================================
// useUser - Get current user profile
// ============================================
export function useUser() {
  const [user, setUser] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    
    async function fetchUser() {
      try {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        if (!authUser) {
          setUser(null);
          return;
        }

        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', authUser.id)
          .single();

        if (error) throw error;
        setUser(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, []);

  return { user, loading, error };
}

// ============================================
// useDeadlines - Get user's deadlines
// ============================================
export function useDeadlines(options?: { 
  platform?: string; 
  status?: string;
  limit?: number;
}) {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDeadlines = useCallback(async () => {
    const supabase = createClient();
    setLoading(true);
    
    try {
      let query = supabase
        .from('deadlines')
        .select('*')
        .order('due_date', { ascending: true });

      if (options?.platform) {
        query = query.eq('platform', options.platform);
      }
      if (options?.status) {
        query = query.eq('status', options.status);
      }
      if (options?.limit) {
        query = query.limit(options.limit);
      }

      // Only get upcoming deadlines by default
      query = query.gte('due_date', new Date().toISOString());

      const { data, error } = await query;

      if (error) throw error;
      setDeadlines(data || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [options?.platform, options?.status, options?.limit]);

  useEffect(() => {
    fetchDeadlines();
  }, [fetchDeadlines]);

  return { deadlines, loading, error, refetch: fetchDeadlines };
}

// ============================================
// useSchedule - Get user's schedule for today
// ============================================
export function useSchedule(date?: Date) {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    const targetDate = date || new Date();
    const dayName = targetDate.toLocaleDateString('en-US', { weekday: 'long' });

    async function fetchSchedule() {
      try {
        const { data, error } = await supabase
          .from('schedule_items')
          .select('*')
          .or(`days.cs.{${dayName}},specific_date.eq.${targetDate.toISOString().split('T')[0]}`)
          .order('start_time', { ascending: true });

        if (error) throw error;
        setSchedule(data || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchSchedule();
  }, [date]);

  return { schedule, loading, error };
}

// ============================================
// usePlatforms - Get platform summaries
// ============================================
export function usePlatforms() {
  const [platforms, setPlatforms] = useState<PlatformSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlatforms = useCallback(async () => {
    const supabase = createClient();
    setLoading(true);

    try {
      // Get user platforms
      const { data: userPlatforms, error: platformError } = await supabase
        .from('user_platforms')
        .select('*');

      if (platformError) throw platformError;

      // Get pending deadline counts per platform
      const { data: deadlineCounts, error: countError } = await supabase
        .from('deadlines')
        .select('platform')
        .eq('status', 'pending')
        .gte('due_date', new Date().toISOString());

      if (countError) throw countError;

      // Count per platform
      const counts: Record<string, number> = {};
      (deadlineCounts || []).forEach(d => {
        counts[d.platform] = (counts[d.platform] || 0) + 1;
      });

      // Build summaries
      const allPlatforms = ['canvas', 'gradescope', 'campuswire', 'prairielearn'];
      const summaries: PlatformSummary[] = allPlatforms.map(p => {
        const userPlatform = userPlatforms?.find(up => up.platform === p);
        return {
          platform: p as PlatformSummary['platform'],
          name: platformNames[p],
          pending_count: counts[p] || 0,
          connected: userPlatform?.connected || false,
          last_synced: userPlatform?.last_synced || null,
          color: platformColors[p],
          label: counts[p] === 1 ? 'pending task' : 'pending tasks',
        };
      });

      setPlatforms(summaries);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlatforms();
  }, [fetchPlatforms]);

  return { platforms, loading, error, refetch: fetchPlatforms };
}

// ============================================
// useCourses - Get user's courses
// ============================================
export function useCourses() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCourses = useCallback(async () => {
    const supabase = createClient();
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('courses')
        .select('*')
        .order('name', { ascending: true });

      if (error) throw error;
      setCourses(data || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  return { courses, loading, error, refetch: fetchCourses };
}

// ============================================
// useSyncStatus - Check if sync is in progress
// ============================================
export function useSyncStatus() {
  const [syncing, setSyncing] = useState(false);
  const [lastJob, setLastJob] = useState<{ platform: string; status: string } | null>(null);

  useEffect(() => {
    const supabase = createClient();

    async function checkStatus() {
      const { data } = await supabase
        .from('scrape_jobs')
        .select('platform, status')
        .in('status', ['pending', 'running'])
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (data) {
        setSyncing(true);
        setLastJob(data);
      } else {
        setSyncing(false);
      }
    }

    checkStatus();

    // Subscribe to changes
    const channel = supabase
      .channel('scrape_jobs_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'scrape_jobs' },
        () => checkStatus()
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return { syncing, lastJob };
}

// ============================================
// triggerSync - Start a sync job
// ============================================
export async function triggerSync(platform?: string) {
  const response = await fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Sync failed');
  }

  return response.json();
}
