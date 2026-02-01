'use client';

import { useParams } from 'next/navigation';
import { createClient } from '@/app/lib/supabase/client';
import { useEffect, useState } from 'react';
import Header from '../../../components/Header';
import { getGreeting, getFormattedDate } from '../../../lib/mockData';
import { useUser } from '../../../lib/hooks/useData';
import { BookOpen, Loader2 } from 'lucide-react';

export default function ClassDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const [classData, setClassData] = useState<{ title: string | null; code: string | null; term: string | null } | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useUser();

  useEffect(() => {
    if (!id) return;
    const supabase = createClient();
    supabase
      .from('classes')
      .select('title, code, term')
      .eq('id', id)
      .single()
      .then(({ data, error }) => {
        if (!error) setClassData(data);
        setLoading(false);
      });
  }, [id]);

  const title = classData?.code && classData?.title ? `${classData.code} – ${classData.title}` : (classData?.title || classData?.code || 'Class');

  return (
    <div className="max-w-7xl mx-auto">
      <Header
        greeting={getGreeting()}
        userName={user?.name || 'Student'}
        date={getFormattedDate()}
      />
      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh] gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading class...</p>
        </div>
      ) : classData ? (
        <div className="mt-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{title}</h1>
              {classData.term && (
                <p className="text-gray-400 text-sm">{classData.term}</p>
              )}
            </div>
          </div>
          <p className="text-gray-500 text-sm">Assignments and details for this class will appear here.</p>
        </div>
      ) : (
        <p className="text-gray-400 mt-6">Class not found.</p>
      )}
    </div>
  );
}
