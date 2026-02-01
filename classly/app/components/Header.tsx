'use client';

import { Bell, Settings, User } from 'lucide-react';

interface HeaderProps {
  greeting: string;
  userName: string;
  date: string;
}

export default function Header({ greeting, userName, date }: HeaderProps) {
  return (
    <header className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-3xl font-bold text-white">
          {greeting}, <span className="text-cyan-400">{userName}</span>
        </h1>
        <p className="text-gray-400 mt-1">{date}</p>
      </div>
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
          <Bell className="w-6 h-6" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-cyan-400 rounded-full"></span>
        </button>
        <button className="p-2 text-gray-400 hover:text-white transition-colors">
          <Settings className="w-6 h-6" />
        </button>
        <button className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </button>
      </div>
    </header>
  );
}
