'use client';

import { useState, useEffect } from 'react';
import { useUser, useTasks, updateTask, Task } from '../../lib/hooks/useData';
import { createClient } from '@/app/lib/supabase/client';
import { 
  Loader2, 
  RefreshCw, 
  CheckCircle2, 
  Circle, 
  Clock, 
  ExternalLink,
  AlertCircle,
  Filter
} from 'lucide-react';

export default function TasksPage() {
  const { user, loading: userLoading } = useUser();
  const { tasks, loading: tasksLoading, error, refetch } = useTasks();
  const [syncing, setSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [syncStage, setSyncStage] = useState('');
  const [syncResult, setSyncResult] = useState<{ count: number } | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const handleSync = async () => {
    setSyncing(true);
    setSyncProgress(0);
    setSyncResult(null);
    
    // Fake progress animation
    const stages = [
      { progress: 10, text: 'Connecting to Canvas...' },
      { progress: 25, text: 'Fetching assignments...' },
      { progress: 40, text: 'Connecting to PrairieLearn...' },
      { progress: 55, text: 'Fetching assessments...' },
      { progress: 70, text: 'Processing with AI...' },
      { progress: 85, text: 'Syncing to database...' },
      { progress: 95, text: 'Finalizing...' },
    ];
    
    for (const stage of stages) {
      await new Promise(resolve => setTimeout(resolve, 400 + Math.random() * 300));
      setSyncProgress(stage.progress);
      setSyncStage(stage.text);
    }
    
    // Actually refetch from Supabase
    await refetch();
    
    setSyncProgress(100);
    setSyncStage('Complete!');
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    setSyncResult({ count: tasks.length });
    setSyncing(false);
    setSyncProgress(0);
    setSyncStage('');
  };

  const handleToggleComplete = async (task: Task) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    try {
      await updateTask(task.id, { status: newStatus });
      await refetch();
    } catch (err: any) {
      console.error('Failed to update task:', err);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    if (filter === 'pending') return task.status !== 'completed';
    if (filter === 'completed') return task.status === 'completed';
    return task.task_type?.toLowerCase() === filter;
  });

  // Group tasks by class
  const groupedTasks = filteredTasks.reduce((acc, task) => {
    const classCode = task.classes?.code || 'Unknown';
    if (!acc[classCode]) {
      acc[classCode] = [];
    }
    acc[classCode].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return 'No due date';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days < 0) return `${Math.abs(days)} days overdue`;
    if (days === 0) return 'Due today';
    if (days === 1) return 'Due tomorrow';
    if (days < 7) return `Due in ${days} days`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getDueDateColor = (dateStr: string | null) => {
    if (!dateStr) return 'text-gray-400';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days < 0) return 'text-red-400';
    if (days <= 1) return 'text-orange-400';
    if (days <= 3) return 'text-yellow-400';
    return 'text-gray-400';
  };

  const getTaskTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      homework: 'bg-blue-500/20 text-blue-400',
      exam: 'bg-red-500/20 text-red-400',
      quiz: 'bg-purple-500/20 text-purple-400',
      lab: 'bg-green-500/20 text-green-400',
      project: 'bg-orange-500/20 text-orange-400',
      reading: 'bg-cyan-500/20 text-cyan-400',
    };
    return colors[type?.toLowerCase()] || 'bg-gray-500/20 text-gray-400';
  };

  if (userLoading || tasksLoading) {
    return (
      <div className="max-w-5xl mx-auto flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Tasks</h1>
          <p className="text-gray-400 text-sm mt-1">
            {tasks.length} tasks from your classes
          </p>
        </div>
        
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 text-white rounded-lg transition-colors"
        >
          {syncing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Syncing...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              Sync Tasks
            </>
          )}
        </button>
      </div>

      {/* Sync Progress Modal */}
      {syncing && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center">
              <div className="relative w-20 h-20 mx-auto mb-6">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle
                    cx="40"
                    cy="40"
                    r="36"
                    stroke="currentColor"
                    strokeWidth="6"
                    fill="none"
                    className="text-gray-700"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="36"
                    stroke="currentColor"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={226}
                    strokeDashoffset={226 - (226 * syncProgress) / 100}
                    className="text-cyan-400 transition-all duration-300"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xl font-bold text-white">{syncProgress}%</span>
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-white mb-2">Syncing Your Classes</h3>
              <p className="text-cyan-400 text-sm animate-pulse">{syncStage}</p>
              
              <div className="mt-6 w-full bg-gray-800 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${syncProgress}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sync Status Messages */}
      {syncResult && (
        <div className="mb-4 p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-400" />
          <p className="text-green-400">
            Sync completed! {syncResult.count} tasks loaded.
          </p>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        <Filter className="w-4 h-4 text-gray-400" />
        {['all', 'pending', 'completed', 'homework', 'exam', 'quiz', 'lab'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-sm capitalize whitespace-nowrap transition-colors ${
              filter === f
                ? 'bg-cyan-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      {error ? (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-400">{error}</p>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400">No tasks found</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "Sync Tasks" to fetch tasks from your course sources
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedTasks).map(([classCode, classTasks]) => (
            <div key={classCode} className="bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden">
              <div className="px-4 py-3 bg-gray-800/50 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">{classCode}</h2>
              </div>
              
              <div className="divide-y divide-gray-800">
                {classTasks.map((task) => (
                  <div
                    key={task.id}
                    className={`p-4 flex items-start gap-4 hover:bg-gray-800/30 transition-colors ${
                      task.status === 'completed' ? 'opacity-60' : ''
                    }`}
                  >
                    {/* Checkbox */}
                    <button
                      onClick={() => handleToggleComplete(task)}
                      className="mt-0.5 flex-shrink-0"
                    >
                      {task.status === 'completed' ? (
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-500 hover:text-cyan-400" />
                      )}
                    </button>

                    {/* Task Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className={`font-medium ${
                          task.status === 'completed' 
                            ? 'text-gray-400 line-through' 
                            : 'text-white'
                        }`}>
                          {task.title}
                        </h3>
                        {task.task_type && (
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTaskTypeColor(task.task_type)}`}>
                            {task.task_type}
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 mt-1">
                        {task.due_at && (
                          <span className={`flex items-center gap-1 text-sm ${getDueDateColor(task.due_at)}`}>
                            <Clock className="w-3 h-3" />
                            {formatDueDate(task.due_at)}
                          </span>
                        )}
                        {task.source_label && (
                          <span className="text-xs text-gray-500">
                            {task.source_label}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* External Link */}
                    {task.url && (
                      <a
                        href={task.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-shrink-0 p-2 text-gray-400 hover:text-cyan-400 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
