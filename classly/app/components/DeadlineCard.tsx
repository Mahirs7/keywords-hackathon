'use client';

import { Calendar, Clock, ChevronRight } from 'lucide-react';
import { Deadline, platformBgColors } from '../lib/mockData';

interface DeadlineCardProps {
  deadline: Deadline;
}

export default function DeadlineCard({ deadline }: DeadlineCardProps) {
  return (
    <div className="bg-[#1a1f26] rounded-xl p-4 border border-gray-800 hover:border-gray-700 transition-all cursor-pointer group">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 text-xs font-medium rounded-md capitalize ${platformBgColors[deadline.platform]}`}>
              {deadline.platform}
            </span>
            <span className="text-xs text-gray-500">{deadline.type}</span>
          </div>
          <h3 className="text-white font-medium mb-1 group-hover:text-cyan-400 transition-colors">
            {deadline.title}
          </h3>
          <p className="text-sm text-gray-500">{deadline.course}</p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-1 text-gray-400 text-sm mb-1">
            <Calendar className="w-4 h-4" />
            <span>{deadline.dueDate}</span>
          </div>
          <div className="flex items-center gap-1 text-gray-500 text-sm">
            <Clock className="w-4 h-4" />
            <span>{deadline.dueTime}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

interface DeadlinesListProps {
  deadlines: Deadline[];
}

export function DeadlinesList({ deadlines }: DeadlinesListProps) {
  return (
    <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
      <div className="flex items-center justify-between p-5 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Upcoming Deadlines</h2>
        <button className="flex items-center gap-1 text-cyan-400 text-sm hover:text-cyan-300 transition-colors">
          View all
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      <div className="p-4 space-y-3">
        {deadlines.map((deadline) => (
          <DeadlineCard key={deadline.id} deadline={deadline} />
        ))}
      </div>
    </div>
  );
}
