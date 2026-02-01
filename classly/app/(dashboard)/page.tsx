'use client';

import Header from '../components/Header';
import PlatformCard from '../components/PlatformCard';
import { DeadlinesList } from '../components/DeadlineCard';
import TodaySchedule from '../components/TodaySchedule';
import AIAssistant from '../components/AIAssistant';
import { 
  mockUser, 
  mockPlatforms, 
  mockDeadlines, 
  mockSchedule,
  getGreeting,
  getFormattedDate 
} from '../lib/mockData';

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <Header 
        greeting={getGreeting()} 
        userName={mockUser.name} 
        date={getFormattedDate()} 
      />

      {/* Platform Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {mockPlatforms.map((platform) => (
          <PlatformCard
            key={platform.id}
            name={platform.name}
            count={platform.count}
            label={platform.label}
            color={platform.color}
          />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Deadlines - Takes 2 columns */}
        <div className="col-span-2">
          <DeadlinesList deadlines={mockDeadlines.slice(0, 4)} />
        </div>

        {/* Right Column - Schedule & AI */}
        <div className="space-y-6">
          <TodaySchedule schedule={mockSchedule} />
          <AIAssistant />
        </div>
      </div>
    </div>
  );
}
