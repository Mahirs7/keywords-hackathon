'use client';

import Header from '../../components/Header';
import { useUser, useDeadlines, useCourses, usePlatforms, triggerSync } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { BookOpen, Calendar, ExternalLink, CheckCircle, AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { useState } from 'react';

export default function CanvasPage() {
  const { user, loading: userLoading } = useUser();
  const { deadlines, loading: deadlinesLoading, refetch: refetchDeadlines } = useDeadlines({ platform: 'canvas' });
  const { courses, loading: coursesLoading } = useCourses();
  const { platforms } = usePlatforms();
  const [syncing, setSyncing] = useState(false);

  const isLoading = userLoading || deadlinesLoading || coursesLoading;

  // Get Canvas-specific data
  const canvasPlatform = platforms.find(p => p.platform === 'canvas');
  const canvasCourses = courses.filter(c => c.platform === 'canvas');
  
  // Count stats
  const pendingCount = deadlines.filter(d => d.status === 'pending').length;
  const submittedCount = deadlines.filter(d => d.status === 'submitted').length;
  const gradedCount = deadlines.filter(d => d.status === 'graded').length;
  const dueThisWeek = deadlines.filter(d => {
    if (!d.due_date) return false;
    const dueDate = new Date(d.due_date);
    const now = new Date();
    const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    return dueDate >= now && dueDate <= weekFromNow;
  }).length;

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync('canvas');
      setTimeout(() => {
        refetchDeadlines();
        setSyncing(false);
      }, 2000);
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading Canvas data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <Header 
        greeting={getGreeting()} 
        userName={user?.name || 'Student'} 
        date={getFormattedDate()} 
      />

      {/* Platform Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Canvas</h2>
            <p className="text-gray-400">{pendingCount} pending tasks across {canvasCourses.length} courses</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {canvasPlatform?.last_synced && (
            <span className="text-sm text-gray-500">
              Last synced: {new Date(canvasPlatform.last_synced).toLocaleTimeString()}
            </span>
          )}
          <button 
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a1f26] text-gray-300 rounded-xl hover:bg-gray-800 transition-colors border border-gray-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>
          <a 
            href="https://canvas.illinois.edu" 
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Open Canvas
          </a>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Pending', value: pendingCount.toString(), color: 'text-orange-400', bg: 'bg-orange-500/10' },
          { label: 'Due This Week', value: dueThisWeek.toString(), color: 'text-red-400', bg: 'bg-red-500/10' },
          { label: 'Submitted', value: submittedCount.toString(), color: 'text-green-400', bg: 'bg-green-500/10' },
          { label: 'Graded', value: gradedCount.toString(), color: 'text-blue-400', bg: 'bg-blue-500/10' },
        ].map((stat, i) => (
          <div key={i} className={`${stat.bg} rounded-xl p-4 border border-gray-800`}>
            <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Assignments List */}
        <div className="col-span-2 bg-[#0f1419] rounded-2xl border border-gray-800">
          <div className="flex items-center justify-between p-5 border-b border-gray-800">
            <h3 className="text-lg font-semibold text-white">Upcoming Assignments</h3>
            <select className="bg-[#1a1f26] text-gray-300 rounded-lg px-3 py-2 border border-gray-700 text-sm">
              <option>All Courses</option>
              {canvasCourses.map(course => (
                <option key={course.id}>{course.code}</option>
              ))}
            </select>
          </div>
          <div className="p-4 space-y-3">
            {deadlines.length > 0 ? (
              deadlines.map((deadline) => (
                <div 
                  key={deadline.id}
                  className="p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {deadline.status === 'submitted' || deadline.status === 'graded' ? (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-orange-400" />
                        )}
                        <h4 className="text-white font-medium group-hover:text-cyan-400 transition-colors">
                          {deadline.title}
                        </h4>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{deadline.course_name}</p>
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1 text-sm text-gray-400">
                          <Calendar className="w-4 h-4" />
                          {deadline.due_date ? new Date(deadline.due_date).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                          }) : 'No due date'}
                        </span>
                        {deadline.points && (
                          <span className="text-sm text-gray-400">{deadline.points} pts</span>
                        )}
                      </div>
                    </div>
                    {deadline.status === 'pending' && (
                      <button className="px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg text-sm hover:bg-cyan-500/20 transition-colors">
                        Start
                      </button>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-400">
                <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No assignments found</p>
                <p className="text-sm mt-1">Sync your Canvas account to see assignments</p>
              </div>
            )}
          </div>
        </div>

        {/* Courses & Grades */}
        <div className="space-y-6">
          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Your Courses</h3>
            <div className="space-y-3">
              {canvasCourses.length > 0 ? (
                canvasCourses.map((course) => (
                  <div 
                    key={course.id}
                    className="p-3 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">{course.code}</p>
                        <p className="text-xs text-gray-500">{course.name}</p>
                      </div>
                      <div className="text-right">
                        {course.grade && (
                          <p className="text-green-400 font-semibold">{course.grade}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-gray-400 text-sm">
                  No courses synced yet
                </div>
              )}
            </div>
          </div>

          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {deadlines.filter(d => d.status === 'graded').slice(0, 3).map((item) => (
                <div 
                  key={item.id}
                  className="p-3 bg-[#1a1f26] rounded-xl border border-gray-800"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">{item.course_name}</p>
                      <p className="text-sm font-medium text-white">{item.title}</p>
                    </div>
                    {item.grade && (
                      <span className="text-green-400 font-semibold">{item.grade}</span>
                    )}
                  </div>
                </div>
              ))}
              {deadlines.filter(d => d.status === 'graded').length === 0 && (
                <div className="text-center py-4 text-gray-400 text-sm">
                  No graded assignments yet
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
