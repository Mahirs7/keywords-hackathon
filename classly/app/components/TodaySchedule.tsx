'use client';

import { ChevronRight } from 'lucide-react';
import { ScheduleItem } from '../lib/mockData';

interface ScheduleItemCardProps {
  item: ScheduleItem;
}

export function ScheduleItemCard({ item }: ScheduleItemCardProps) {
  return (
    <div className="flex items-start gap-3">
      {/* Timeline dot */}
      <div className="flex flex-col items-center">
        <div className={`w-2 h-2 rounded-full mt-2 ${item.isActive ? 'bg-cyan-400' : 'bg-gray-600'}`}></div>
        <div className="w-px h-full bg-gray-700 mt-1"></div>
      </div>
      
      {/* Card */}
      <div
        className={`flex-1 rounded-xl p-4 mb-3 transition-all cursor-pointer ${
          item.isActive
            ? 'bg-cyan-500/20 border border-cyan-500/30'
            : 'bg-[#1a1f26] border border-gray-800 hover:border-gray-700'
        }`}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-gray-400 mb-1">{item.startTime}</p>
            <h3 className={`font-medium ${item.isActive ? 'text-cyan-400' : 'text-white'}`}>
              {item.title}
            </h3>
            {item.location && (
              <p className="text-xs text-gray-500 mt-1">{item.location}</p>
            )}
          </div>
          <span className="text-xs text-gray-500 bg-gray-800/50 px-2 py-1 rounded">
            {item.duration}
          </span>
        </div>
      </div>
    </div>
  );
}

interface TodayScheduleProps {
  schedule: ScheduleItem[];
}

export default function TodaySchedule({ schedule }: TodayScheduleProps) {
  return (
    <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
      <div className="flex items-center justify-between p-5 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Today&apos;s Schedule</h2>
        <button className="flex items-center gap-1 text-cyan-400 text-sm hover:text-cyan-300 transition-colors">
          Edit
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      <div className="p-4">
        {schedule.map((item) => (
          <ScheduleItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
