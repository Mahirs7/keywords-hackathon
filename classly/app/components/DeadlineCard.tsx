'use client';

import { BookOpen, ClipboardCheck, MessageCircle, Code, Clock } from 'lucide-react';

// Generic deadline interface for the component
interface DeadlineDisplay {
  id: string;
  title: string;
  course: string;
  platform: string;
  type: string;
  dueDate: string;
  dueTime: string;
  status: string;
}

interface DeadlineCardProps {
  deadline: DeadlineDisplay;
}

const platformStyles: Record<DeadlineDisplay['platform'], { label: string; classes: string; icon: React.ReactNode }> = {
  canvas: {
    label: 'Canvas',
    classes: 'text-red-400 bg-red-500/10',
    icon: <BookOpen className="w-4 h-4" />,
  },
  gradescope: {
    label: 'Gradescope',
    classes: 'text-green-400 bg-green-500/10',
    icon: <ClipboardCheck className="w-4 h-4" />,
  },
  campuswire: {
    label: 'Campuswire',
    classes: 'text-blue-400 bg-blue-500/10',
    icon: <MessageCircle className="w-4 h-4" />,
  },
  prairielearn: {
    label: 'PrairieLearn',
    classes: 'text-purple-400 bg-purple-500/10',
    icon: <Code className="w-4 h-4" />,
  },
};

function DeadlineCard({ deadline }: DeadlineCardProps) {
  // Normalize platform to lowercase for lookup
  const platformKey = deadline.platform?.toLowerCase() as DeadlineDisplay['platform'];
  const platform = platformStyles[platformKey] || platformStyles.canvas; // fallback to canvas

  return (
    <div className="bg-[#1a1f26] border border-gray-800 rounded-2xl p-4 hover:border-gray-700 transition-all">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${platform.classes}`}>
            {platform.icon}
          </div>
          <div>
            <h3 className="text-white font-medium leading-snug">{deadline.title}</h3>
            <p className="text-xs text-gray-500 mt-1">{deadline.course}</p>
          </div>
        </div>
        <span className="text-xs text-gray-400 bg-gray-800/60 px-2 py-1 rounded">
          {deadline.type}
        </span>
      </div>

      <div className="flex items-center justify-between mt-4">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Clock className="w-4 h-4" />
          <span>
            {deadline.dueDate} · {deadline.dueTime}
          </span>
        </div>
        <span className="text-xs text-gray-400">{platform.label}</span>
      </div>
    </div>
  );
}

interface DeadlinesListProps {
  deadlines: DeadlineDisplay[];
}

export function DeadlinesList({ deadlines }: DeadlinesListProps) {
  return (
    <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
      <div className="flex items-center justify-between p-5 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Upcoming Deadlines</h2>
        <button className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
          View all
        </button>
      </div>
      <div className="p-4 space-y-4">
        {deadlines.length > 0 ? (
          deadlines.map((deadline) => (
            <DeadlineCard key={deadline.id} deadline={deadline} />
          ))
        ) : (
          <div className="text-center py-8 text-gray-400">
            <Clock className="w-8 h-8 mx-auto mb-3 opacity-50" />
            <p>No upcoming deadlines</p>
            <p className="text-sm mt-1">Connect your platforms to see assignments</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DeadlineCard;
