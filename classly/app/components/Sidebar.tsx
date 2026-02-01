'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  LayoutDashboard, 
  Calendar, 
  BookOpen, 
  Settings,
  ChevronLeft,
  LogOut,
  Bot,
  Sparkles,
  ClipboardCheck,
  MessageCircle
} from 'lucide-react';
import { createClient } from '@/app/lib/supabase/client';
import { useClasses } from '@/app/lib/hooks/useData';

const navItems = [
  { href: '/home', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/schedule', label: 'Schedule', icon: Calendar },
  { href: '/ai', label: 'AI', icon: Bot },
];

const platforms = [
  { href: '/canvas', label: 'Canvas', icon: BookOpen, count: 4, color: 'bg-red-500' },
  { href: '/gradescope', label: 'Gradescope', icon: ClipboardCheck, count: 2, color: 'bg-green-500' },
  { href: '/campuswire', label: 'Campuswire', icon: MessageCircle, count: 8, color: 'bg-blue-500' },
  { href: '/assistant', label: 'Course Assistant', icon: Sparkles },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { classes, loading: classesLoading } = useClasses();
  
  // Try to create Supabase client, but handle gracefully if not configured
  let supabase;
  try {
    supabase = createClient();
  } catch (error) {
    console.warn('Supabase not configured:', error);
    supabase = null;
  }

  const handleLogout = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
    router.push('/login');
    router.refresh();
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-[#0f1419] border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-800">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
          <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <span className="text-xl font-bold text-white">Classly</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}

        {/* Classes section */}
        <div className="pt-6">
          <p className="px-4 mb-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Classes
          </p>
          {classesLoading ? (
            <div className="px-4 py-3 text-gray-500 text-sm">Loading...</div>
          ) : classes.length === 0 ? (
            <Link
              href="/home?addClasses=1"
              className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-cyan-400 hover:bg-cyan-500/10"
            >
              <Plus className="w-5 h-5" />
              <span className="font-medium">Add classes</span>
            </Link>
          ) : (
            classes.map((cls) => {
              const label = cls.code && cls.title ? `${cls.code} – ${cls.title}` : (cls.title || cls.code || 'Untitled');
              const isActive = pathname === `/classes/${cls.id}`;
              return (
                <Link
                  key={cls.id}
                  href={`/classes/${cls.id}`}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400'
                      : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                  }`}
                >
                  <BookOpen className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium truncate" title={label}>{label}</span>
                </Link>
              );
            })
          )}
        </div>
      </nav>

      {/* Settings & Logout */}
      <div className="px-4 py-4 border-t border-gray-800 space-y-2">
        <Link
          href="/settings"
          className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
            pathname === '/settings'
              ? 'bg-cyan-500/10 text-cyan-400'
              : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
          }`}
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-gray-400 hover:bg-red-500/10 hover:text-red-400"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Sign out</span>
        </button>
      </div>
    </aside>
  );
}
