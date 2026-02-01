'use client';

import { useState } from 'react';
import Header from '../../components/Header';
import { useUser, usePlatforms, triggerSync } from '../../lib/hooks/useData';
import { getGreeting, getFormattedDate } from '../../lib/mockData';
import { 
  BookOpen, 
  ClipboardCheck, 
  MessageCircle, 
  GraduationCap,
  RefreshCw,
  Check,
  X,
  Loader2,
  Settings,
  Bell,
  User,
  Shield
} from 'lucide-react';

const platformConfig = {
  canvas: {
    name: 'Canvas',
    icon: BookOpen,
    color: 'red',
    description: 'Access assignments, grades, and announcements from Canvas LMS',
  },
  gradescope: {
    name: 'Gradescope',
    icon: ClipboardCheck,
    color: 'green',
    description: 'Track homework submissions and grades from Gradescope',
  },
  campuswire: {
    name: 'Campuswire',
    icon: MessageCircle,
    color: 'blue',
    description: 'Stay updated with class discussions and Q&A',
  },
  prairielearn: {
    name: 'PrairieLearn',
    icon: GraduationCap,
    color: 'purple',
    description: 'Monitor quizzes and assessments from PrairieLearn',
  },
};

export default function SettingsPage() {
  const { user } = useUser();
  const { platforms, refetch: refetchPlatforms } = usePlatforms();
  const [syncing, setSyncing] = useState<string | null>(null);

  const handleSync = async (platform: string) => {
    setSyncing(platform);
    try {
      await triggerSync(platform);
      // Wait a bit then refetch
      setTimeout(() => {
        refetchPlatforms();
        setSyncing(null);
      }, 2000);
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncing(null);
    }
  };

  const handleSyncAll = async () => {
    setSyncing('all');
    try {
      await triggerSync();
      setTimeout(() => {
        refetchPlatforms();
        setSyncing(null);
      }, 3000);
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncing(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Header 
        greeting={getGreeting()} 
        userName={user?.name || 'Student'} 
        date={getFormattedDate()} 
      />

      <div className="space-y-6">
        {/* Platform Connections */}
        <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
          <div className="flex items-center justify-between p-5 border-b border-gray-800">
            <div>
              <h2 className="text-lg font-semibold text-white">Platform Connections</h2>
              <p className="text-sm text-gray-400 mt-1">Connect your learning platforms to sync data</p>
            </div>
            <button
              onClick={handleSyncAll}
              disabled={syncing !== null}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg hover:bg-cyan-500/20 transition disabled:opacity-50"
            >
              {syncing === 'all' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              Sync All
            </button>
          </div>

          <div className="p-5 space-y-4">
            {Object.entries(platformConfig).map(([key, config]) => {
              const Icon = config.icon;
              const platformData = platforms.find(p => p.platform === key);
              const isConnected = platformData?.connected;
              const lastSynced = platformData?.last_synced;
              const isSyncing = syncing === key;

              return (
                <div
                  key={key}
                  className="flex items-center justify-between p-4 bg-[#1a1f26] rounded-xl border border-gray-800"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl bg-${config.color}-500/10`}>
                      <Icon className={`w-6 h-6 text-${config.color}-400`} />
                    </div>
                    <div>
                      <h3 className="text-white font-medium">{config.name}</h3>
                      <p className="text-xs text-gray-500 mt-0.5">{config.description}</p>
                      {lastSynced && (
                        <p className="text-xs text-gray-400 mt-1">
                          Last synced: {new Date(lastSynced).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {isConnected ? (
                      <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded">
                        <Check className="w-3 h-3" />
                        Connected
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-gray-400 bg-gray-500/10 px-2 py-1 rounded">
                        <X className="w-3 h-3" />
                        Not connected
                      </span>
                    )}
                    <button
                      onClick={() => handleSync(key)}
                      disabled={syncing !== null}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition disabled:opacity-50"
                    >
                      {isSyncing ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <RefreshCw className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Account Settings */}
        <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
          <div className="p-5 border-b border-gray-800">
            <h2 className="text-lg font-semibold text-white">Account</h2>
          </div>
          <div className="p-5 space-y-4">
            <div className="flex items-center justify-between p-4 bg-[#1a1f26] rounded-xl border border-gray-800">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gray-500/10">
                  <User className="w-6 h-6 text-gray-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Profile</h3>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </div>
              <button className="text-sm text-cyan-400 hover:text-cyan-300">Edit</button>
            </div>

            <div className="flex items-center justify-between p-4 bg-[#1a1f26] rounded-xl border border-gray-800">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gray-500/10">
                  <Bell className="w-6 h-6 text-gray-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Notifications</h3>
                  <p className="text-xs text-gray-500">Manage email and push notifications</p>
                </div>
              </div>
              <button className="text-sm text-cyan-400 hover:text-cyan-300">Configure</button>
            </div>

            <div className="flex items-center justify-between p-4 bg-[#1a1f26] rounded-xl border border-gray-800">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gray-500/10">
                  <Shield className="w-6 h-6 text-gray-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">Privacy & Security</h3>
                  <p className="text-xs text-gray-500">Password, 2FA, and data settings</p>
                </div>
              </div>
              <button className="text-sm text-cyan-400 hover:text-cyan-300">Manage</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
