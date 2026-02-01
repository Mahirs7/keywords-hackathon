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

    // Get user's Microsoft credentials from profiles
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('msft_email, msft_password')
      .eq('id', user.id)
      .single();

    if (profileError || !profile?.msft_email || !profile?.msft_password) {
      return NextResponse.json(
        { error: 'Microsoft credentials not found. Please add your credentials first.' },
        { status: 400 }
      );
    }

    // Create scrape jobs for all platforms
    const platforms = ['canvas', 'gradescope', 'campuswire', 'prairielearn'];
    const jobs = [];

    for (const platform of platforms) {
      const { data, error } = await supabase
        .from('scrape_jobs')
        .insert({
          user_id: user.id,
          platform,
          status: 'pending',
        })
        .select()
        .single();

      if (error) {
        console.error(`Failed to create job for ${platform}:`, error);
        continue;
      }
      jobs.push(data);
    }

    // Trigger the backend scraper (Flask API)
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';
    
    try {
      const response = await fetch(`${backendUrl}/api/scrape/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          platforms: platforms,
          job_ids: jobs.map(j => j.id),
          credentials: {
            email: profile.msft_email,
            password: profile.msft_password,
          },
        }),
      });

      if (!response.ok) {
        console.error('Backend scraper returned error:', await response.text());
      }
    } catch (backendError) {
      console.error('Failed to trigger backend scraper:', backendError);
      // Don't fail the request - jobs are created, backend will process later
    }

    return NextResponse.json({
      success: true,
      message: 'Course sync initiated',
      jobs: jobs.map(j => ({ id: j.id, platform: j.platform })),
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
