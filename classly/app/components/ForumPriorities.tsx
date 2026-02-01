'use client';

import { MessageSquare, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

interface ForumInsight {
  id: string;
  course: string;
  courseCode: string;
  summary: string;
  sentiment: 'difficult' | 'easy' | 'urgent' | 'tip';
  mentions: number;
}

// Mock forum insights based on course discussions
const forumInsights: ForumInsight[] = [
  {
    id: '1',
    course: 'System Programming',
    courseCode: 'CS 341',
    summary: 'MP is very difficult - many students struggling with memory management',
    sentiment: 'difficult',
    mentions: 24,
  },
  {
    id: '2',
    course: 'Database Systems',
    courseCode: 'CS 411',
    summary: '"Cat\'s Out of the Bag" assignment doesn\'t take too long if you start early',
    sentiment: 'easy',
    mentions: 18,
  },
  {
    id: '3',
    course: 'Probability & Statistics',
    courseCode: 'CS 361',
    summary: 'Midterm covers chapters 1-5, focus on conditional probability',
    sentiment: 'tip',
    mentions: 31,
  },
];

const sentimentConfig = {
  difficult: {
    icon: AlertTriangle,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    label: 'Challenging',
  },
  easy: {
    icon: Clock,
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
    label: 'Manageable',
  },
  urgent: {
    icon: TrendingUp,
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
    label: 'Urgent',
  },
  tip: {
    icon: MessageSquare,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
    label: 'Study Tip',
  },
};

export default function ForumPriorities() {
  return (
    <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
      <div className="flex items-center justify-between p-5 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-semibold text-white">Priorities</h2>
        </div>
        <span className="text-xs text-gray-500">From course forums</span>
      </div>
      <div className="p-4 space-y-3">
        {forumInsights.map((insight) => {
          const config = sentimentConfig[insight.sentiment];
          const Icon = config.icon;
          
          return (
            <div
              key={insight.id}
              className={`rounded-xl p-4 ${config.bg} border ${config.border} transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${config.bg}`}>
                  <Icon className={`w-4 h-4 ${config.color}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-cyan-400">{insight.courseCode}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${config.bg} ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-200 leading-relaxed">
                    {insight.summary}
                  </p>
                  <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                    <MessageSquare className="w-3 h-3" />
                    {insight.mentions} students discussing
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
