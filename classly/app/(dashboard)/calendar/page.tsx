'use client';

import Header from '../../components/Header';
import { useUser, useDeadlines, useSchedule } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { ChevronLeft, ChevronRight, Loader2, Calendar as CalendarIcon } from 'lucide-react';
import { useState } from 'react';

export default function CalendarPage() {
  const { user, loading: userLoading } = useUser();
  const { deadlines, loading: deadlinesLoading } = useDeadlines({});
  const { schedule, loading: scheduleLoading } = useSchedule();
  
  const [currentDate, setCurrentDate] = useState(new Date());

  const isLoading = userLoading || deadlinesLoading || scheduleLoading;

  // Get calendar data
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startingDay = firstDay.getDay();
  const totalDays = lastDay.getDate();

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December'];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Get deadlines for a specific day
  const getDeadlinesForDay = (day: number) => {
    const targetDate = new Date(year, month, day);
    return deadlines.filter(d => {
      if (!d.due_date) return false;
      const dueDate = new Date(d.due_date);
      return dueDate.getFullYear() === targetDate.getFullYear() &&
             dueDate.getMonth() === targetDate.getMonth() &&
             dueDate.getDate() === targetDate.getDate();
    });
  };

  // Check if a day is today
  const isToday = (day: number) => {
    const today = new Date();
    return day === today.getDate() && 
           month === today.getMonth() && 
           year === today.getFullYear();
  };

  // Generate calendar days
  const calendarDays = [];
  for (let i = 0; i < startingDay; i++) {
    calendarDays.push(null);
  }
  for (let i = 1; i <= totalDays; i++) {
    calendarDays.push(i);
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading calendar...</p>
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

      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Calendar</h2>
          <p className="text-gray-400">View all your deadlines and events</p>
        </div>
      </div>

      {/* Month Navigation */}
      <div className="flex items-center justify-between mb-6 bg-[#1a1f26] rounded-xl p-4 border border-gray-800">
        <button 
          onClick={prevMonth}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="text-center">
          <p className="text-white font-semibold text-xl">{monthNames[month]} {year}</p>
          <button 
            onClick={goToToday}
            className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            Today
          </button>
        </div>
        <button 
          onClick={nextMonth}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Calendar Grid */}
        <div className="col-span-2 bg-[#0f1419] rounded-2xl border border-gray-800 overflow-hidden">
          {/* Day Headers */}
          <div className="grid grid-cols-7 border-b border-gray-800">
            {dayNames.map((day) => (
              <div key={day} className="p-4 text-center text-gray-400 text-sm font-medium">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Days */}
          <div className="grid grid-cols-7">
            {calendarDays.map((day, index) => {
              const dayDeadlines = day ? getDeadlinesForDay(day) : [];
              return (
                <div 
                  key={index}
                  className={`min-h-[100px] p-2 border-b border-r border-gray-800/50 ${
                    day ? 'hover:bg-gray-800/30 cursor-pointer' : ''
                  } ${isToday(day || 0) ? 'bg-cyan-500/10' : ''}`}
                >
                  {day && (
                    <>
                      <p className={`text-sm font-medium mb-1 ${
                        isToday(day) ? 'text-cyan-400' : 'text-white'
                      }`}>
                        {day}
                      </p>
                      <div className="space-y-1">
                        {dayDeadlines.slice(0, 2).map((deadline) => (
                          <div 
                            key={deadline.id}
                            className={`text-xs p-1 rounded truncate ${
                              deadline.platform === 'canvas' 
                                ? 'bg-red-500/20 text-red-400' 
                                : deadline.platform === 'gradescope'
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-blue-500/20 text-blue-400'
                            }`}
                          >
                            {deadline.title}
                          </div>
                        ))}
                        {dayDeadlines.length > 2 && (
                          <p className="text-xs text-gray-500">+{dayDeadlines.length - 2} more</p>
                        )}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Upcoming Deadlines Sidebar */}
        <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
          <h3 className="text-lg font-semibold text-white mb-4">Upcoming Deadlines</h3>
          <div className="space-y-3">
            {deadlines.length > 0 ? (
              deadlines.slice(0, 6).map((deadline) => (
                <div 
                  key={deadline.id}
                  className="p-3 bg-[#1a1f26] rounded-xl border border-gray-800"
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-2 h-2 mt-2 rounded-full ${
                      deadline.platform === 'canvas' ? 'bg-red-500' :
                      deadline.platform === 'gradescope' ? 'bg-green-500' :
                      'bg-blue-500'
                    }`}></div>
                    <div className="flex-1">
                      <p className="text-white font-medium text-sm">{deadline.title}</p>
                      <p className="text-xs text-gray-500">{deadline.course_name}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {deadline.due_date ? new Date(deadline.due_date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit'
                        }) : 'No due date'}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <CalendarIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No upcoming deadlines</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
