'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '../../components/Header';
import PlatformCard from '../../components/PlatformCard';
import { DeadlinesList } from '../../components/DeadlineCard';
import TodaySchedule from '../../components/TodaySchedule';
import AIAssistant from '../../components/AIAssistant';
import AddClassesModal from '../../components/AddClassesModal';
import { useUser, useDeadlines, useSchedule, usePlatforms, useCourses, useSyncStatus, useTasks } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { RefreshCw, Loader2 } from 'lucide-react';

export default function Dashboard() {
  const [showAddClassesModal, setShowAddClassesModal] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get('addClasses') === '1') {
      setShowAddClassesModal(true);
    }
  }, [searchParams]);

  const { user, loading: userLoading } = useUser();
  const { tasks, loading: tasksLoading, refetch: refetchTasks } = useTasks();
  const { schedule, loading: scheduleLoading } = useSchedule();
  const { platforms, loading: platformsLoading, refetch: refetchPlatforms } = usePlatforms();
  const { courses, loading: coursesLoading, refetch: refetchCourses } = useCourses();
  const { syncing } = useSyncStatus();

  const isLoading = userLoading || tasksLoading || scheduleLoading || platformsLoading || coursesLoading;

  // Transform tasks for DeadlinesList component
  const transformedDeadlines = tasks.slice(0, 5).map(t => ({
    id: t.id,
    title: t.title,
    course: t.classes?.code || 'Unknown',
    platform: t.source_label || 'Canvas',
    type: t.task_type || 'Assignment',
    dueDate: t.due_at ? new Date(t.due_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'No date',
    dueTime: t.due_at ? new Date(t.due_at).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : '',
    status: t.status === 'completed' ? 'submitted' : 'pending',
  }));

  // Get tasks due today for schedule
  const today = new Date();
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const todayEnd = new Date(todayStart.getTime() + 24 * 60 * 60 * 1000);
  
  const todayTasks = tasks.filter(t => {
    if (!t.due_at) return false;
    const dueDate = new Date(t.due_at);
    return dueDate >= todayStart && dueDate < todayEnd;
  });

  // Combine schedule items with today's tasks
  const transformedSchedule = [
    ...schedule.map(s => ({
      id: s.id,
      title: s.title,
      type: s.type,
      startTime: s.start_time ? s.start_time.slice(0, 5) : '',
      duration: s.duration_minutes ? `${Math.floor(s.duration_minutes / 60)}h ${s.duration_minutes % 60}m` : '',
      location: s.location || undefined,
      color: s.color,
      isActive: false,
    })),
    ...todayTasks.map(t => ({
      id: t.id,
      title: `📋 ${t.title}`,
      type: t.task_type || 'task',
      startTime: t.due_at ? new Date(t.due_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '',
      duration: 'Due',
      location: t.classes?.code,
      color: '#06b6d4',
      isActive: true,
    }))
  ].sort((a, b) => a.startTime.localeCompare(b.startTime));

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
            <RefreshCw className="w-4 h-4" />
            Sync
          </button>
        </div>
      </div>

      {/* Platform Summary Cards */}
      {transformedPlatforms.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          {transformedPlatforms.map((platform) => (
            <PlatformCard
              key={platform.id}
              name={platform.name}
              count={platform.count}
              label={platform.label}
              color={platform.color}
            />
          ))}
        </div>
      )}

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
          refetchTasks();
        }}
      />
    </div>
  );
}
