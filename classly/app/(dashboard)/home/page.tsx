'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '../../components/Header';
import PlatformCard from '../../components/PlatformCard';
import { DeadlinesList } from '../../components/DeadlineCard';
import TodaySchedule from '../../components/TodaySchedule';
import AIAssistant from '../../components/AIAssistant';
import AddClassesModal from '../../components/AddClassesModal';
import { useUser, useDeadlines, useSchedule, usePlatforms, useCourses, useSyncStatus } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { RefreshCw, Loader2, Plus } from 'lucide-react';

export default function Dashboard() {
  const [showAddClassesModal, setShowAddClassesModal] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get('addClasses') === '1') {
      setShowAddClassesModal(true);
    }
  }, [searchParams]);

  const { user, loading: userLoading } = useUser();
  const { deadlines, loading: deadlinesLoading, refetch: refetchDeadlines } = useDeadlines({ limit: 4, status: 'pending' });
  const { schedule, loading: scheduleLoading } = useSchedule();
  const { platforms, loading: platformsLoading, refetch: refetchPlatforms } = usePlatforms();
  const { courses, loading: coursesLoading, refetch: refetchCourses } = useCourses();
  const { syncing } = useSyncStatus();

  const isLoading = userLoading || deadlinesLoading || scheduleLoading || platformsLoading || coursesLoading;

  // Transform data for components (maintain backwards compatibility)
  const transformedDeadlines = deadlines.map(d => ({
    id: d.id,
    title: d.title,
    course: d.course_name || 'Unknown Course',
    platform: d.platform,
    type: d.type || 'Assignment',
    dueDate: d.due_date ? new Date(d.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'No date',
    dueTime: d.due_date ? new Date(d.due_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : '',
    status: d.status,
  }));

  const transformedSchedule = schedule.map(s => ({
    id: s.id,
    title: s.title,
    type: s.type,
    startTime: s.start_time ? s.start_time.slice(0, 5) : '',
    duration: s.duration_minutes ? `${Math.floor(s.duration_minutes / 60)}h ${s.duration_minutes % 60}m` : '',
    location: s.location || undefined,
    color: s.color,
    isActive: false, // TODO: calculate based on current time
  }));

  const transformedPlatforms = platforms.map(p => ({
    id: p.platform,
    name: p.name,
    count: p.pending_count,
    label: p.label,
    color: p.color,
  }));

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Header 
          greeting={getGreeting()} 
          userName={user?.name || 'Student'} 
          date={getFormattedDate()} 
        />
        <div className="flex items-center gap-3">
          {syncing && (
            <div className="flex items-center gap-2 text-sm text-cyan-400 bg-cyan-500/10 px-3 py-2 rounded-lg">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Syncing...
            </div>
          )}
          <button
            onClick={() => setShowAddClassesModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Classes
          </button>
        </div>
      </div>

      {/* Platform Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {transformedPlatforms.length > 0 ? (
          transformedPlatforms.map((platform) => (
            <PlatformCard
              key={platform.id}
              name={platform.name}
              count={platform.count}
              label={platform.label}
              color={platform.color}
            />
          ))
        ) : (
          <div className="col-span-3 text-center py-8 text-gray-400">
            <p>No platforms connected yet.</p>
            <p className="text-sm mt-1">Connect Canvas, Gradescope, or other platforms to see your tasks.</p>
          </div>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Deadlines - Takes 2 columns */}
        <div className="col-span-2">
          <DeadlinesList deadlines={transformedDeadlines} />
        </div>

        {/* Right Column - Schedule & AI */}
        <div className="space-y-6">
          <TodaySchedule schedule={transformedSchedule} />
          <AIAssistant />
        </div>
      </div>

      {/* Add Classes Modal */}
      <AddClassesModal 
        isOpen={showAddClassesModal} 
        onClose={() => setShowAddClassesModal(false)}
        onSuccess={() => {
          refetchCourses();
          refetchPlatforms();
          refetchDeadlines();
        }}
      />
    </div>
  );
}
