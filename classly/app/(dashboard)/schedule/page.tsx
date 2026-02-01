'use client';

import Header from '../../components/Header';
import { mockUser, mockSchedule, getGreeting, getFormattedDate } from '../../lib/mockData';
import { Plus, ChevronLeft, ChevronRight, Clock, MapPin } from 'lucide-react';
import { useState } from 'react';

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const timeSlots = ['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM'];

export default function SchedulePage() {
  const [currentWeek, setCurrentWeek] = useState('Jan 27 - Feb 2, 2026');

  return (
    <div className="max-w-7xl mx-auto">
      <Header 
        greeting={getGreeting()} 
        userName={mockUser.name} 
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
                i === 4 ? 'bg-cyan-500/10' : ''
              }`}
            >
              <p className="text-gray-400 text-sm">{day}</p>
              <p className={`text-lg font-semibold ${i === 4 ? 'text-cyan-400' : 'text-white'}`}>
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
              {weekDays.map((day, i) => (
                <div 
                  key={`${day}-${time}`} 
                  className={`p-2 border-l border-gray-800/50 min-h-[60px] hover:bg-gray-800/30 transition-colors ${
                    i === 4 ? 'bg-cyan-500/5' : ''
                  }`}
                >
                  {/* Example events */}
                  {time === '9 AM' && (day === 'Mon' || day === 'Wed' || day === 'Fri') && (
                    <div className="bg-blue-500/20 border-l-2 border-blue-500 rounded-r px-2 py-1 text-xs">
                      <p className="text-blue-400 font-medium">CS 101 Lecture</p>
                      <p className="text-gray-500">Siebel 1404</p>
                    </div>
                  )}
                  {time === '2 PM' && (day === 'Tue' || day === 'Thu') && (
                    <div className="bg-green-500/20 border-l-2 border-green-500 rounded-r px-2 py-1 text-xs">
                      <p className="text-green-400 font-medium">MATH 201</p>
                      <p className="text-gray-500">Altgeld 314</p>
                    </div>
                  )}
                  {time === '10 AM' && day === 'Fri' && (
                    <div className="bg-purple-500/20 border-l-2 border-purple-500 rounded-r px-2 py-1 text-xs">
                      <p className="text-purple-400 font-medium">Study Session</p>
                      <p className="text-gray-500">Dynamic Prog.</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Events Sidebar */}
      <div className="mt-6 grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
          <h3 className="text-lg font-semibold text-white mb-4">This Week&apos;s Classes</h3>
          <div className="space-y-3">
            {[
              { name: 'CS 101 - Intro to Computer Science', time: 'MWF 9:00 AM', location: 'Siebel 1404', color: 'bg-blue-500' },
              { name: 'MATH 201 - Calculus II', time: 'TTh 2:00 PM', location: 'Altgeld 314', color: 'bg-green-500' },
              { name: 'PSYC 100 - Intro to Psychology', time: 'MWF 11:00 AM', location: 'Lincoln 1000', color: 'bg-orange-500' },
              { name: 'CS 444 - Deep Learning', time: 'TTh 3:30 PM', location: 'Siebel 2405', color: 'bg-purple-500' },
            ].map((cls, i) => (
              <div key={i} className="flex items-center gap-4 p-4 bg-[#1a1f26] rounded-xl border border-gray-800">
                <div className={`w-2 h-12 rounded-full ${cls.color}`}></div>
                <div className="flex-1">
                  <p className="text-white font-medium">{cls.name}</p>
                  <div className="flex items-center gap-4 mt-1">
                    <span className="flex items-center gap-1 text-sm text-gray-400">
                      <Clock className="w-4 h-4" />
                      {cls.time}
                    </span>
                    <span className="flex items-center gap-1 text-sm text-gray-400">
                      <MapPin className="w-4 h-4" />
                      {cls.location}
                    </span>
                  </div>
                </div>
              </div>
            ))}
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
