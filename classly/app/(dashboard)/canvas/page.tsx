'use client';

import Header from '../../components/Header';
import { mockUser, mockCanvasAssignments, getGreeting, getFormattedDate } from '../../lib/mockData';
import { BookOpen, Calendar, Clock, ExternalLink, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function CanvasPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <Header 
        greeting={getGreeting()} 
        userName={mockUser.name} 
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
            <p className="text-gray-400">4 pending tasks across 3 courses</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">Last synced: 5 min ago</span>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1a1f26] text-gray-300 rounded-xl hover:bg-gray-800 transition-colors border border-gray-700">
            <RefreshCw className="w-4 h-4" />
            Sync Now
          </button>
          <a 
            href="https://canvas.illinois.edu" 
            target="_blank"
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
          { label: 'Pending', value: '4', color: 'text-orange-400', bg: 'bg-orange-500/10' },
          { label: 'Due This Week', value: '3', color: 'text-red-400', bg: 'bg-red-500/10' },
          { label: 'Submitted', value: '12', color: 'text-green-400', bg: 'bg-green-500/10' },
          { label: 'Graded', value: '8', color: 'text-blue-400', bg: 'bg-blue-500/10' },
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
              <option>CS 101</option>
              <option>MATH 201</option>
              <option>PSYC 100</option>
            </select>
          </div>
          <div className="p-4 space-y-3">
            {mockCanvasAssignments.map((assignment) => (
              <div 
                key={assignment.id}
                className="p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {assignment.submitted ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-orange-400" />
                      )}
                      <h4 className="text-white font-medium group-hover:text-cyan-400 transition-colors">
                        {assignment.title}
                      </h4>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">{assignment.course}</p>
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1 text-sm text-gray-400">
                        <Calendar className="w-4 h-4" />
                        {new Date(assignment.dueDate).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                      </span>
                      <span className="text-sm text-gray-400">{assignment.points} pts</span>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg text-sm hover:bg-cyan-500/20 transition-colors">
                    Start
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Courses & Grades */}
        <div className="space-y-6">
          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Your Courses</h3>
            <div className="space-y-3">
              {[
                { name: 'CS 101', full: 'Intro to Computer Science', grade: 'A-', pending: 2 },
                { name: 'MATH 201', full: 'Calculus II', grade: 'B+', pending: 1 },
                { name: 'PSYC 100', full: 'Intro to Psychology', grade: 'A', pending: 1 },
                { name: 'CS 444', full: 'Deep Learning', grade: 'A-', pending: 0 },
              ].map((course, i) => (
                <div 
                  key={i}
                  className="p-3 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">{course.name}</p>
                      <p className="text-xs text-gray-500">{course.full}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-semibold">{course.grade}</p>
                      {course.pending > 0 && (
                        <p className="text-xs text-orange-400">{course.pending} pending</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Announcements</h3>
            <div className="space-y-3">
              {[
                { course: 'CS 101', title: 'Midterm Exam Details', time: '2 hours ago', unread: true },
                { course: 'MATH 201', title: 'Office Hours Change', time: '1 day ago', unread: false },
              ].map((ann, i) => (
                <div 
                  key={i}
                  className={`p-3 rounded-xl border transition-colors cursor-pointer ${
                    ann.unread 
                      ? 'bg-cyan-500/10 border-cyan-500/30' 
                      : 'bg-[#1a1f26] border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">{ann.course}</p>
                      <p className={`text-sm font-medium ${ann.unread ? 'text-cyan-400' : 'text-white'}`}>
                        {ann.title}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500">{ann.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
