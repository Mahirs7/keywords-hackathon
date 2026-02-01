'use client';

import { BookOpen, ClipboardCheck, MessageCircle } from 'lucide-react';

interface PlatformCardProps {
  name: string;
  count: number;
  label: string;
  color: string;
}

const iconMap: Record<string, React.ReactNode> = {
  Canvas: <BookOpen className="w-6 h-6" />,
  Gradescope: <ClipboardCheck className="w-6 h-6" />,
  Campuswire: <MessageCircle className="w-6 h-6" />,
};

const colorMap: Record<string, string> = {
  Canvas: 'text-red-400 bg-red-500/10',
  Gradescope: 'text-green-400 bg-green-500/10',
  Campuswire: 'text-blue-400 bg-blue-500/10',
};

export default function PlatformCard({ name, count, label, color }: PlatformCardProps) {
  return (
    <div className="bg-[#1a1f26] rounded-2xl p-5 border border-gray-800 hover:border-gray-700 transition-all cursor-pointer">
      <div className="flex items-start gap-4">
        <div className={`p-3 rounded-xl ${colorMap[name] || 'text-gray-400 bg-gray-500/10'}`}>
          {iconMap[name]}
        </div>
        <div>
          <p className="text-sm text-gray-400 mb-1">{name}</p>
          <p className="text-3xl font-bold text-white">{count}</p>
          <p className="text-sm text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}
