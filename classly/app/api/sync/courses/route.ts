import { createClient } from '@/app/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    
    // Get current user
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Trigger backend: get user's courses + course_sources from Supabase, run scrapers, save assignments
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';

    let jobId: string | null = null;
    try {
      const response = await fetch(`${backendUrl}/api/scrape/sync-from-courses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id }),
      });
      const data = await response.json().catch(() => ({}));
      jobId = data.job_id ?? null;
      if (!response.ok) {
        return NextResponse.json(
          { error: data.error || 'Failed to start sync from courses' },
          { status: response.status }
        );
      }
    } catch (backendError) {
      console.error('Failed to trigger backend sync-from-courses:', backendError);
      return NextResponse.json(
        { error: 'Backend unavailable. Is the Flask server running?' },
        { status: 502 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Sync from your courses started',
      job_id: jobId,
    });

  } catch (error: any) {
    console.error('Sync courses error:', error);
    return NextResponse.json(
      { error: 'Failed to initiate course sync' },
      { status: 500 }
    );
  }
}

// GET - Check sync status
export async function GET(request: Request) {
  try {
    const supabase = await createClient();
    
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get recent scrape jobs
    const { data: jobs, error } = await supabase
      .from('scrape_jobs')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(10);

    if (error) {
      throw error;
    }

    // Check if any jobs are still running
    const activeJobs = jobs?.filter(j => j.status === 'pending' || j.status === 'running') || [];
    const completedJobs = jobs?.filter(j => j.status === 'completed') || [];
    const failedJobs = jobs?.filter(j => j.status === 'failed') || [];

    return NextResponse.json({
      syncing: activeJobs.length > 0,
      activeJobs,
      completedJobs,
      failedJobs,
    });

  } catch (error: any) {
    console.error('Check sync status error:', error);
    return NextResponse.json(
      { error: 'Failed to check sync status' },
      { status: 500 }
    );
  }
}
