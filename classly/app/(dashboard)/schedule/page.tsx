'use client';

import Header from '../../components/Header';
import { useUser, useSchedule, useCourses } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { Plus, ChevronLeft, ChevronRight, Clock, MapPin, Loader2 } from 'lucide-react';
import { useState } from 'react';

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const timeSlots = ['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM'];

export default function SchedulePage() {
  const { user, loading: userLoading } = useUser();
  const { schedule, loading: scheduleLoading } = useSchedule();
  const { courses, loading: coursesLoading } = useCourses();
  const [currentWeek, setCurrentWeek] = useState('Jan 27 - Feb 2, 2026');

  const isLoading = userLoading || scheduleLoading || coursesLoading;

  // Get today's day index (0 = Monday, 6 = Sunday)
  const today = new Date();
  const todayIndex = (today.getDay() + 6) % 7;

  // Transform schedule items for the calendar
  const getEventsForSlot = (dayIndex: number, timeSlot: string) => {
    const hour = parseInt(timeSlot.split(' ')[0]) + (timeSlot.includes('PM') && !timeSlot.includes('12') ? 12 : 0);
    return schedule.filter(item => {
      if (!item.day_of_week || !item.start_time) return false;
      const itemDay = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].indexOf(item.day_of_week.toLowerCase());
      const itemHour = parseInt(item.start_time.split(':')[0]);
      return itemDay === dayIndex && itemHour === hour;
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading schedule...</p>
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

      {/* Schedule Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Weekly Schedule</h2>
          <p className="text-gray-400">Manage your classes and study sessions</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500 text-white rounded-xl hover:bg-cyan-600 transition-colors">
          <Plus className="w-5 h-5" />
          Add Event
        </button>
      </div>

      {/* Week Navigation */}
      <div className="flex items-center justify-between mb-6 bg-[#1a1f26] rounded-xl p-4 border border-gray-800">
        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="text-center">
          <p className="text-white font-semibold">{currentWeek}</p>
          <button className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
            Today
          </button>
        </div>
        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="bg-[#0f1419] rounded-2xl border border-gray-800 overflow-hidden">
        {/* Day Headers */}
        <div className="grid grid-cols-8 border-b border-gray-800">
          <div className="p-4 text-gray-500 text-sm"></div>
          {weekDays.map((day, i) => (
            <div 
              key={day} 
              className={`p-4 text-center border-l border-gray-800 ${
                i === todayIndex ? 'bg-cyan-500/10' : ''
              }`}
            >
              <p className="text-gray-400 text-sm">{day}</p>
              <p className={`text-lg font-semibold ${i === todayIndex ? 'text-cyan-400' : 'text-white'}`}>
                {27 + i > 31 ? 27 + i - 31 : 27 + i}
              </p>
            </div>
          ))}
        </div>

        {/* Time Grid */}
        <div className="max-h-[600px] overflow-y-auto">
          {timeSlots.map((time) => (
            <div key={time} className="grid grid-cols-8 border-b border-gray-800/50">
              <div className="p-4 text-gray-500 text-sm flex items-start">{time}</div>
              {weekDays.map((day, i) => {
                const events = getEventsForSlot(i, time);
                return (
                  <div 
                    key={`${day}-${time}`} 
                    className={`p-2 border-l border-gray-800/50 min-h-[60px] hover:bg-gray-800/30 transition-colors ${
                      i === todayIndex ? 'bg-cyan-500/5' : ''
                    }`}
                  >
                    {events.map((event) => (
                      <div 
                        key={event.id}
                        className={`${event.color || 'bg-blue-500/20'} border-l-2 border-blue-500 rounded-r px-2 py-1 text-xs mb-1`}
                      >
                        <p className="text-white font-medium">{event.title}</p>
                        {event.location && (
                          <p className="text-gray-400">{event.location}</p>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Courses & Quick Add */}
      <div className="mt-6 grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
          <h3 className="text-lg font-semibold text-white mb-4">Your Courses</h3>
          <div className="space-y-3">
            {courses.length > 0 ? (
              courses.map((course) => (
                <div key={course.id} className="flex items-center gap-4 p-4 bg-[#1a1f26] rounded-xl border border-gray-800">
                  <div className={`w-2 h-12 rounded-full ${course.color || 'bg-blue-500'}`}></div>
                  <div className="flex-1">
                    <p className="text-white font-medium">{course.code} - {course.name}</p>
                    <div className="flex items-center gap-4 mt-1">
                      {course.schedule && (
                        <span className="flex items-center gap-1 text-sm text-gray-400">
                          <Clock className="w-4 h-4" />
                          {course.schedule}
                        </span>
                      )}
                      {course.location && (
                        <span className="flex items-center gap-1 text-sm text-gray-400">
                          <MapPin className="w-4 h-4" />
                          {course.location}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>No courses added yet.</p>
                <p className="text-sm mt-1">Add classes to see them here.</p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Add</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-cyan-500/50 transition-colors">
              <p className="text-white font-medium">📚 Study Session</p>
              <p className="text-sm text-gray-500">Block time for focused study</p>
            </button>
            <button className="w-full text-left p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-cyan-500/50 transition-colors">
              <p className="text-white font-medium">👥 Office Hours</p>
              <p className="text-sm text-gray-500">Add TA or professor hours</p>
            </button>
            <button className="w-full text-left p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-cyan-500/50 transition-colors">
              <p className="text-white font-medium">☕ Break</p>
              <p className="text-sm text-gray-500">Schedule a break</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
