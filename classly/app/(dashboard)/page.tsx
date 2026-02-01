'use client';

<<<<<<< HEAD:classly/app/(dashboard)/page.tsx
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
=======
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  BookOpen,
  ClipboardCheck,
  MessageCircle,
  GraduationCap,
  ArrowRight,
  CheckCircle2,
  Calendar,
  BarChart3,
  Clock,
  Zap,
  TrendingUp,
  Bell,
  RefreshCw,
  X,
  Menu,
  Github,
  Mail,
  Shield,
  Sparkles,
  Layers,
  Target,
  Rocket
} from 'lucide-react';

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0);
  const [counters, setCounters] = useState({ assignments: 0, platforms: 0, students: 0 });
  const [isVisible, setIsVisible] = useState(false);
  const statsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
          animateCounters();
        }
      },
      { threshold: 0.3 }
    );
    if (statsRef.current) observer.observe(statsRef.current);
    return () => observer.disconnect();
  }, []);

  const animateCounters = () => {
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;

    const animate = (key: 'assignments' | 'platforms' | 'students', target: number) => {
      let current = 0;
      const increment = target / steps;
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          setCounters(prev => ({ ...prev, [key]: target }));
          clearInterval(timer);
        } else {
          setCounters(prev => ({ ...prev, [key]: Math.floor(current) }));
        }
      }, interval);
    };

    animate('assignments', 150);
    animate('platforms', 4);
    animate('students', 1000);
  };

  const platforms = [
    { name: 'Canvas', icon: BookOpen, color: 'red', x: '10%', y: '20%' },
    { name: 'Gradescope', icon: ClipboardCheck, color: 'green', x: '80%', y: '30%' },
    { name: 'Campuswire', icon: MessageCircle, color: 'blue', x: '15%', y: '70%' },
    { name: 'PrairieLearn', icon: GraduationCap, color: 'purple', x: '85%', y: '75%' },
  ];
>>>>>>> 928bc8714ec0f9639933592aadf90ec9e20c4cdd:classly/app/page.tsx

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* Background Grid */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#1a1a2e_1px,transparent_1px),linear-gradient(to_bottom,#1a1a2e_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-20 pointer-events-none" />
      
      {/* Animated Gradient Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute w-[600px] h-[600px] bg-cyan-500/20 rounded-full blur-3xl"
          style={{ 
            transform: `translate(${scrollY * 0.1}px, ${scrollY * 0.1}px)`,
            left: '-300px',
            top: '-300px'
          }}
        />
        <div 
          className="absolute w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-3xl"
          style={{ 
            transform: `translate(${-scrollY * 0.15}px, ${scrollY * 0.1}px)`,
            right: '-250px',
            top: '200px'
          }}
        />
        <div 
          className="absolute w-[400px] h-[400px] bg-blue-500/15 rounded-full blur-3xl"
          style={{ 
            transform: `translate(${scrollY * 0.08}px, ${-scrollY * 0.12}px)`,
            left: '50%',
            bottom: '-200px'
          }}
        />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/20 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                <Layers className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Classly
              </span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="text-gray-400 hover:text-white transition-colors">How It Works</a>
              <Link href="/dashboard" className="text-gray-400 hover:text-white transition-colors">Dashboard</Link>
              <Link 
                href="/dashboard"
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg font-medium hover:from-cyan-400 hover:to-blue-400 transition-all hover:scale-105"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-16 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Content */}
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="text-sm text-gray-300">Built for Students, by Students</span>
              </div>
              
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
                  All Your Coursework.
                </span>
                <br />
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                  One Dashboard.
                </span>
              </h1>

              <p className="text-xl md:text-2xl text-gray-400 leading-relaxed">
                Canvas. Gradescope. Campuswire. PrairieLearn.
                <br />
                <span className="text-gray-300">Unified in one beautiful interface.</span>
              </p>

              <p className="text-lg text-gray-500 max-w-xl">
                Stop juggling between multiple tabs and platforms. See all your assignments, deadlines, and grades in one place. Never miss a due date again.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link 
                  href="/dashboard"
                  className="group px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-semibold text-lg hover:from-cyan-400 hover:to-blue-400 transition-all hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/50 flex items-center justify-center gap-2"
                >
                  Get Started Free
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl font-semibold text-lg hover:bg-white/10 transition-all hover:scale-105">
                  View Demo
                </button>
              </div>
            </div>

            {/* Right: Dashboard Preview */}
            <div className="relative">
              <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 shadow-2xl">
                {/* Mock Dashboard UI */}
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-center justify-between pb-4 border-b border-white/10">
                    <div>
                      <div className="h-4 w-32 bg-white/20 rounded mb-2" />
                      <div className="h-3 w-24 bg-white/10 rounded" />
                    </div>
                    <div className="flex gap-2">
                      <div className="w-8 h-8 rounded-lg bg-white/10" />
                      <div className="w-8 h-8 rounded-lg bg-white/10" />
                    </div>
                  </div>

                  {/* Platform Cards */}
                  <div className="grid grid-cols-3 gap-3">
                    {['Canvas', 'Gradescope', 'Campuswire'].map((name, i) => (
                      <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/10">
                        <div className="h-3 w-16 bg-white/20 rounded mb-2" />
                        <div className="h-6 w-8 bg-white/10 rounded" />
                      </div>
                    ))}
                  </div>

                  {/* Deadlines List */}
                  <div className="space-y-2">
                    <div className="h-3 w-24 bg-white/20 rounded mb-3" />
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/10">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="h-3 w-32 bg-white/20 rounded mb-2" />
                            <div className="h-2 w-24 bg-white/10 rounded" />
                          </div>
                          <div className="h-6 w-16 bg-white/10 rounded" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Floating Platform Badges */}
              {platforms.map((platform, i) => {
                const Icon = platform.icon;
                return (
                  <div
                    key={i}
                    className={`absolute ${platform.color === 'red' ? 'bg-red-500/20 border-red-500/30 text-red-400' : platform.color === 'green' ? 'bg-green-500/20 border-green-500/30 text-green-400' : platform.color === 'blue' ? 'bg-blue-500/20 border-blue-500/30 text-blue-400' : 'bg-purple-500/20 border-purple-500/30 text-purple-400'} backdrop-blur-sm border rounded-full p-3 shadow-lg animate-float`}
                    style={{ 
                      left: platform.x, 
                      top: platform.y,
                      animationDelay: `${i * 0.2}s`
                    }}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Problem → Solution Section */}
      <section className="relative py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            {/* Left: Problems */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/20">
                <X className="w-4 h-4 text-red-400" />
                <span className="text-sm text-red-400 font-medium">The Problem</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold">
                Too Many Tabs.
                <br />
                Too Many Deadlines.
                <br />
                <span className="text-gray-400">Too Much Stress.</span>
              </h2>
              <div className="space-y-4 pt-4">
                {[
                  { icon: X, text: 'Constantly switching between 4+ platforms' },
                  { icon: Calendar, text: 'Missing deadlines buried in different systems' },
                  { icon: Layers, text: 'No unified view of your coursework' },
                  { icon: Target, text: 'Context switching kills productivity' },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={i} className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all group">
                      <div className="p-2 rounded-lg bg-red-500/10 group-hover:bg-red-500/20 transition-colors">
                        <Icon className="w-5 h-5 text-red-400" />
                      </div>
                      <p className="text-gray-300 flex-1">{item.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Solutions */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400 font-medium">The Solution</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold">
                One Dashboard.
                <br />
                <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  Everything Unified.
                </span>
              </h2>
              <div className="space-y-4 pt-4">
                {[
                  { icon: Layers, text: 'All platforms in one beautiful interface' },
                  { icon: Calendar, text: 'Unified deadline timeline you can trust' },
                  { icon: BarChart3, text: 'Quick overview of all your coursework' },
                  { icon: Zap, text: 'AI assistant to help you stay organized' },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={i} className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all group">
                      <div className="p-2 rounded-lg bg-green-500/10 group-hover:bg-green-500/20 transition-colors">
                        <Icon className="w-5 h-5 text-green-400" />
                      </div>
                      <p className="text-gray-300 flex-1">{item.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Get started in three simple steps. No complex setup, no hassle.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Connector Lines */}
            <div className="hidden md:block absolute top-24 left-1/3 right-1/3 h-0.5 bg-gradient-to-r from-cyan-500/50 via-blue-500/50 to-purple-500/50" />

            {[
              {
                step: '1',
                title: 'Connect Platforms',
                description: 'Link your Canvas, Gradescope, Campuswire, and PrairieLearn accounts securely with one-click authentication.',
                icon: Layers,
                gradient: 'from-cyan-500 to-cyan-600'
              },
              {
                step: '2',
                title: 'Sync Deadlines',
                description: 'We automatically pull all your assignments, deadlines, and course information. Everything stays up-to-date.',
                icon: RefreshCw,
                gradient: 'from-blue-500 to-blue-600'
              },
              {
                step: '3',
                title: 'Stay Organized',
                description: 'View everything in one beautiful dashboard. Never miss a deadline, track your progress, and stay ahead.',
                icon: Rocket,
                gradient: 'from-purple-500 to-purple-600'
              },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} className="relative">
                  <div className="text-8xl font-bold text-white/5 absolute -top-8 -left-4">{item.step}</div>
                  <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all group">
                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${item.gradient} p-4 mb-6 group-hover:scale-110 transition-transform`}>
                      <Icon className="w-full h-full text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Feature Grid Section */}
      <section id="features" className="relative py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Everything You Need
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Powerful features designed to make your student life easier.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Calendar,
                title: 'Unified Deadlines',
                description: 'See all assignments from every platform in one timeline. Never miss a due date again.',
                gradient: 'from-cyan-500 to-blue-500'
              },
              {
                icon: Clock,
                title: 'Smart Schedule',
                description: 'Your daily schedule with class times, study blocks, and deadlines all integrated seamlessly.',
                gradient: 'from-purple-500 to-pink-500'
              },
              {
                icon: BarChart3,
                title: 'Platform Overview',
                description: 'Quick stats from Canvas, Gradescope, Campuswire, and PrairieLearn at a glance.',
                gradient: 'from-green-500 to-emerald-500'
              },
              {
                icon: Zap,
                title: 'AI Study Assistant',
                description: 'Get instant help with your coursework. Ask questions, get reminders, and stay organized.',
                gradient: 'from-yellow-500 to-orange-500'
              },
              {
                icon: TrendingUp,
                title: 'Grade Tracking',
                description: 'Monitor your grades and progress across all platforms in real-time with beautiful visualizations.',
                gradient: 'from-blue-500 to-cyan-500'
              },
              {
                icon: Bell,
                title: 'Sync & Notifications',
                description: 'Automatically syncs with all your platforms. Get notified about upcoming deadlines and new assignments.',
                gradient: 'from-indigo-500 to-purple-500'
              },
            ].map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={i}
                  className="group relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:border-white/20 transition-all hover:scale-105 hover:shadow-2xl"
                >
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} p-3 mb-6 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-full h-full text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity -z-10`} />
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Live Dashboard Preview */}
      <section className="relative py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              See It In Action
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              A real dashboard built for real students.
            </p>
          </div>

          {/* Mock Dashboard */}
          <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 md:p-12 shadow-2xl overflow-hidden">
            <div className="grid md:grid-cols-3 gap-6 mb-6">
              {[
                { name: 'Canvas', count: 4, label: 'pending tasks', icon: BookOpen, bgColor: 'bg-red-500/10', iconColor: 'text-red-400' },
                { name: 'Gradescope', count: 2, label: 'submissions due', icon: ClipboardCheck, bgColor: 'bg-green-500/10', iconColor: 'text-green-400' },
                { name: 'Campuswire', count: 8, label: 'new posts', icon: MessageCircle, bgColor: 'bg-blue-500/10', iconColor: 'text-blue-400' },
              ].map((platform, i) => {
                const Icon = platform.icon;
                return (
                  <div key={i} className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className={`w-12 h-12 rounded-lg ${platform.bgColor} flex items-center justify-center`}>
                        <Icon className={`w-6 h-6 ${platform.iconColor}`} />
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">{platform.name}</p>
                        <p className="text-2xl font-bold">{platform.count}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{platform.label}</p>
                  </div>
                );
              })}
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2 backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Upcoming Deadlines</h3>
                <div className="space-y-3">
                  {['Problem Set 4', 'Lab 5', 'Homework 6'].map((title, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/10">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{title}</p>
                          <p className="text-sm text-gray-400">CS 101</p>
                        </div>
                        <div className="text-sm text-gray-400">Feb {4 + i}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4">Today's Schedule</h3>
                  <div className="space-y-3">
                    {['CS 101 Lecture', 'Study Session', 'MATH 201'].map((item, i) => (
                      <div key={i} className="p-3 bg-white/5 rounded-lg">
                        <p className="text-sm font-medium">{item}</p>
                        <p className="text-xs text-gray-400">9:00 AM - 10:15 AM</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-4">AI Assistant</h3>
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="text-sm text-gray-300">Ready to help with your coursework!</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div ref={statsRef} className="grid md:grid-cols-3 gap-8 mt-16">
            {[
              { value: counters.assignments, suffix: '+', label: 'Assignments Tracked', sublabel: 'Across all platforms', gradient: 'from-cyan-400 to-blue-400' },
              { value: counters.platforms, suffix: '', label: 'Platforms Integrated', sublabel: 'One unified dashboard', gradient: 'from-purple-400 to-pink-400' },
              { value: counters.students, suffix: '+', label: 'Students Served', sublabel: 'And growing daily', gradient: 'from-green-400 to-emerald-400' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className={`text-6xl font-bold mb-4 bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent`}>
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-xl text-gray-300 font-semibold mb-2">{stat.label}</div>
                <div className="text-gray-500">{stat.sublabel}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="relative py-24 px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 backdrop-blur-sm border border-white/10 mb-8">
            <Rocket className="w-5 h-5 text-cyan-400" />
            <span className="text-gray-300">Built at Keywords Hackathon 2026</span>
          </div>
          <blockquote className="text-2xl md:text-3xl font-medium text-gray-200 mb-6">
            "Finally, a tool that understands how students actually work. Classly has saved me hours every week."
          </blockquote>
          <p className="text-gray-400">— Student, University of Illinois</p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative py-24 px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="backdrop-blur-xl bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20 border border-white/10 rounded-3xl p-12 md:p-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Simplify Your Student Life?
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Join thousands of students who've already made the switch to Classly. Get started in seconds.
            </p>
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-2 px-10 py-5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-semibold text-xl hover:from-cyan-400 hover:to-blue-400 transition-all hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/50"
            >
              Get Started Free
              <ArrowRight className="w-6 h-6" />
            </Link>
            <p className="text-sm text-gray-400 mt-6">
              No credit card required • Free forever • Privacy-first
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 lg:px-8 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                <Layers className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold">Classly</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:text-white transition-colors">
                <Github className="w-4 h-4" />
                GitHub
              </a>
              <a href="mailto:hello@classly.app" className="flex items-center gap-2 hover:text-white transition-colors">
                <Mail className="w-4 h-4" />
                Contact
              </a>
              <a href="#" className="flex items-center gap-2 hover:text-white transition-colors">
                <Shield className="w-4 h-4" />
                Privacy
              </a>
            </div>
          </div>
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>© 2026 Classly. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
