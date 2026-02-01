'use client';

import Header from '../../components/Header';
import { useUser, useDeadlines, useCourses, usePlatforms, triggerSync } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { ClipboardCheck, Calendar, ExternalLink, CheckCircle, AlertCircle, RefreshCw, Upload, Loader2 } from 'lucide-react';
import { useState } from 'react';

export default function GradescopePage() {
  const { user, loading: userLoading } = useUser();
  const { deadlines, loading: deadlinesLoading, refetch: refetchDeadlines } = useDeadlines({ platform: 'gradescope' });
  const { courses, loading: coursesLoading } = useCourses();
  const { platforms } = usePlatforms();
  const [syncing, setSyncing] = useState(false);

  const isLoading = userLoading || deadlinesLoading || coursesLoading;

  // Get Gradescope-specific data
  const gradescopePlatform = platforms.find(p => p.platform === 'gradescope');
  const gradescopeCourses = courses.filter(c => c.platform === 'gradescope');
  
  // Count stats
  const pendingCount = deadlines.filter(d => d.status === 'pending').length;
  const submittedCount = deadlines.filter(d => d.status === 'submitted').length;
  const gradedCount = deadlines.filter(d => d.status === 'graded').length;

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync('gradescope');
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
          <p className="text-gray-400">Loading Gradescope data...</p>
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
          <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
            <ClipboardCheck className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Gradescope</h2>
            <p className="text-gray-400">{pendingCount} submissions due</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {gradescopePlatform?.last_synced && (
            <span className="text-sm text-gray-500">
              Last synced: {new Date(gradescopePlatform.last_synced).toLocaleTimeString()}
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
            href="https://gradescope.com" 
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Open Gradescope
          </a>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Due Soon', value: pendingCount.toString(), color: 'text-orange-400', bg: 'bg-orange-500/10' },
          { label: 'Submitted', value: submittedCount.toString(), color: 'text-green-400', bg: 'bg-green-500/10' },
          { label: 'Graded', value: gradedCount.toString(), color: 'text-blue-400', bg: 'bg-blue-500/10' },
          { label: 'Regrade Requests', value: '0', color: 'text-purple-400', bg: 'bg-purple-500/10' },
        ].map((stat, i) => (
          <div key={i} className={`${stat.bg} rounded-xl p-4 border border-gray-800`}>
            <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Assignments */}
        <div className="col-span-2 bg-[#0f1419] rounded-2xl border border-gray-800">
          <div className="flex items-center justify-between p-5 border-b border-gray-800">
            <h3 className="text-lg font-semibold text-white">Submissions</h3>
            <div className="flex gap-2">
              <button className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-lg text-sm">Due</button>
              <button className="px-3 py-1 text-gray-400 hover:bg-gray-800 rounded-lg text-sm">All</button>
              <button className="px-3 py-1 text-gray-400 hover:bg-gray-800 rounded-lg text-sm">Graded</button>
            </div>
          </div>
          <div className="p-4 space-y-3">
            {deadlines.filter(d => d.status === 'pending').length > 0 ? (
              deadlines.filter(d => d.status === 'pending').map((sub) => (
                <div 
                  key={sub.id}
                  className="p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-5 h-5 text-orange-400" />
                        <h4 className="text-white font-medium">{sub.title}</h4>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{sub.course_name}</p>
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1 text-sm text-gray-400">
                          <Calendar className="w-4 h-4" />
                          Due {sub.due_date ? new Date(sub.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'No date'}
                        </span>
                      </div>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg text-sm hover:bg-green-600 transition-colors">
                      <Upload className="w-4 h-4" />
                      Submit
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <ClipboardCheck className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No pending submissions</p>
              </div>
            )}

            {/* Graded Assignments */}
            {deadlines.filter(d => d.status === 'graded').length > 0 && (
              <div className="pt-4 border-t border-gray-800">
                <p className="text-gray-500 text-sm mb-3">Recently Graded</p>
                {deadlines.filter(d => d.status === 'graded').slice(0, 3).map((item) => (
                  <div 
                    key={item.id}
                    className="p-4 bg-[#1a1f26] rounded-xl border border-gray-800 mb-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <div>
                          <h4 className="text-white font-medium">{item.title}</h4>
                          <p className="text-sm text-gray-500">{item.course_name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        {item.grade && (
                          <p className="text-green-400 font-semibold">{item.grade}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Late Days</h3>
            <div className="text-center py-4">
              <p className="text-5xl font-bold text-cyan-400 mb-2">3</p>
              <p className="text-gray-400">remaining this semester</p>
            </div>
            <div className="bg-[#1a1f26] rounded-xl p-3 mt-4">
              <p className="text-sm text-gray-400">
                <span className="text-yellow-400">Tip:</span> Save your late days for larger assignments closer to midterms.
              </p>
            </div>
          </div>

          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Grade Distribution</h3>
            <div className="space-y-3">
              {gradescopeCourses.length > 0 ? (
                gradescopeCourses.map((course) => (
                  <div key={course.id} className="bg-[#1a1f26] rounded-xl p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">{course.code}</span>
                      {course.grade && (
                        <span className="text-green-400 font-semibold">{course.grade}</span>
                      )}
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-cyan-500 to-green-500 rounded-full"
                        style={{ width: '85%' }}
                      ></div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400 text-sm">
                  No courses synced yet
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
