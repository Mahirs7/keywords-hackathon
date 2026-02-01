import { redirect } from 'next/navigation';
import { createClient } from '@/app/lib/supabase/server';

export default async function RootPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    redirect('/login');
  }
  
  // Redirect to the dashboard route which has the proper layout with sidebar
  redirect('/home');
}
