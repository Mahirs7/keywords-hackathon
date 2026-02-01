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

    const body = await request.json().catch(() => ({}));
    const { platform } = body;

    // Create a scrape job
    const platforms = platform 
      ? [platform] 
      : ['canvas', 'gradescope', 'campuswire', 'prairielearn'];

    const jobs = [];
    for (const p of platforms) {
      const { data, error } = await supabase
        .from('scrape_jobs')
        .insert({
          user_id: user.id,
          platform: p,
          status: 'pending',
        })
        .select()
        .single();

      if (error) {
        console.error(`Failed to create job for ${p}:`, error);
        continue;
      }
      jobs.push(data);
    }

    // Trigger the backend scraper (Flask API)
    // In production, this would be a proper job queue
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';
    
    try {
      await fetch(`${backendUrl}/api/scrape/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
        },
        body: JSON.stringify({
          user_id: user.id,
          platforms: platforms,
          job_ids: jobs.map(j => j.id),
        }),
      });
    } catch (backendError) {
      console.error('Failed to trigger backend scraper:', backendError);
      // Don't fail the request - jobs are created, backend will pick them up
    }

    return NextResponse.json({ 
      message: 'Sync started',
      jobs: jobs.map(j => ({ id: j.id, platform: j.platform, status: j.status })),
    });
  } catch (error: any) {
    console.error('Sync error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET(request: Request) {
  try {
    const supabase = await createClient();
    
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get recent sync jobs
    const { data: jobs, error } = await supabase
      .from('scrape_jobs')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(10);

    if (error) throw error;

    return NextResponse.json({ jobs });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
