'use client';

import { useParams } from 'next/navigation';
import { createClient } from '@/app/lib/supabase/client';
import { useEffect, useState, useRef } from 'react';
import Header from '../../../components/Header';
import { getGreeting, getFormattedDate } from '../../../lib/mockData';
import { useUser } from '../../../lib/hooks/useData';
import { 
  BookOpen, 
  Loader2, 
  MapPin, 
  Clock, 
  Calendar,
  ExternalLink,
  CheckCircle2,
  Circle,
  Send,
  Bot,
  Sparkles,
  Link as LinkIcon,
  ClipboardList
} from 'lucide-react';

interface ClassData {
  id: string;
  title: string | null;
  code: string | null;
  term: string | null;
  location: string | null;
  meeting_times: string | null;
  created_at: string | null;
}

interface ClassSource {
  id: string;
  source_type: string;
  url: string;
  auth_hint: string | null;
}

interface Task {
  id: string;
  title: string;
  task_type: string;
  due_at: string | null;
  url: string | null;
  status: string;
  source_label: string | null;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function ClassDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const [classData, setClassData] = useState<ClassData | null>(null);
  const [sources, setSources] = useState<ClassSource[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useUser();
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    const supabase = createClient();
    
    // Fetch class data
    const fetchData = async () => {
      setLoading(true);
      
      // Get class info
      const { data: classInfo } = await supabase
        .from('classes')
        .select('*')
        .eq('id', id)
        .single();
      
      if (classInfo) {
        setClassData(classInfo);
        
        // Get sources
        const { data: sourcesData } = await supabase
          .from('class_sources')
          .select('*')
          .eq('class_id', id);
        setSources(sourcesData || []);
        
        // Get tasks
        const { data: tasksData } = await supabase
          .from('tasks')
          .select('*')
          .eq('class_id', id)
          .order('due_at', { ascending: true, nullsFirst: false });
        setTasks(tasksData || []);
      }
      
      setLoading(false);
    };
    
    fetchData();
  }, [id]);

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;
    
    const userMessage = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          course_context: classData?.code || classData?.title,
        }),
      });
      
      const data = await response.json();
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || "I couldn't process that. Try again!"
      }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I'm having trouble connecting. Please try again."
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const toggleTaskStatus = async (taskId: string, currentStatus: string) => {
    const supabase = createClient();
    const newStatus = currentStatus === 'completed' ? 'not_started' : 'completed';
    
    await supabase
      .from('tasks')
      .update({ status: newStatus })
      .eq('id', taskId);
    
    setTasks(prev => prev.map(t => 
      t.id === taskId ? { ...t, status: newStatus } : t
    ));
  };

  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return 'No due date';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getDueDateColor = (dateStr: string | null) => {
    if (!dateStr) return 'text-gray-400';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days < 0) return 'text-red-400';
    if (days <= 1) return 'text-orange-400';
    if (days <= 3) return 'text-yellow-400';
    return 'text-gray-400';
  };

  const getSourceIcon = (type: string) => {
    const icons: Record<string, string> = {
      canvas: '🎨',
      prairielearn: '🧪',
      gradescope: '📝',
      campuswire: '💬',
      website: '🌐',
    };
    return icons[type?.toLowerCase()] || '🔗';
  };

  const title = classData?.code && classData?.title 
    ? `${classData.code} – ${classData.title}` 
    : (classData?.title || classData?.code || 'Class');

  const pendingTasks = tasks.filter(t => t.status !== 'completed');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <Header greeting={getGreeting()} userName={user?.name || 'Student'} date={getFormattedDate()} />
        <div className="flex items-center justify-center min-h-[40vh] gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          <p className="text-gray-400">Loading class...</p>
        </div>
      </div>
    );
  }

  if (!classData) {
    return (
      <div className="max-w-7xl mx-auto">
        <Header greeting={getGreeting()} userName={user?.name || 'Student'} date={getFormattedDate()} />
        <p className="text-gray-400 mt-6">Class not found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <Header greeting={getGreeting()} userName={user?.name || 'Student'} date={getFormattedDate()} />
      
      {/* Class Header */}
      <div className="mt-6 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-2xl border border-cyan-500/20 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-cyan-500/20 flex items-center justify-center">
              <BookOpen className="w-7 h-7 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{title}</h1>
              <div className="flex items-center gap-4 mt-2">
                {classData.term && (
                  <span className="flex items-center gap-1 text-sm text-gray-400">
                    <Calendar className="w-4 h-4" />
                    {classData.term}
                  </span>
                )}
                {classData.meeting_times && (
                  <span className="flex items-center gap-1 text-sm text-gray-400">
                    <Clock className="w-4 h-4" />
                    {classData.meeting_times}
                  </span>
                )}
                {classData.location && (
                  <span className="flex items-center gap-1 text-sm text-gray-400">
                    <MapPin className="w-4 h-4" />
                    {classData.location}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="flex gap-4">
            <div className="text-center px-4 py-2 bg-gray-800/50 rounded-xl">
              <p className="text-2xl font-bold text-cyan-400">{pendingTasks.length}</p>
              <p className="text-xs text-gray-400">Pending</p>
            </div>
            <div className="text-center px-4 py-2 bg-gray-800/50 rounded-xl">
              <p className="text-2xl font-bold text-green-400">{completedTasks.length}</p>
              <p className="text-xs text-gray-400">Completed</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 mt-6">
        {/* Main Content - Tasks */}
        <div className="col-span-2 space-y-6">
          {/* Connected Sources */}
          {sources.length > 0 && (
            <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <LinkIcon className="w-5 h-5 text-cyan-400" />
                Connected Sources
              </h2>
              <div className="flex flex-wrap gap-3">
                {sources.map((source) => (
                  <a
                    key={source.id}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 hover:bg-gray-800 rounded-xl border border-gray-700 transition-colors"
                  >
                    <span>{getSourceIcon(source.source_type)}</span>
                    <span className="text-white text-sm">{source.source_type}</span>
                    <ExternalLink className="w-3 h-3 text-gray-400" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Tasks */}
          <div className="bg-[#0f1419] rounded-2xl border border-gray-800 p-5">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-cyan-400" />
              Assignments & Tasks
              <span className="text-sm font-normal text-gray-400">({tasks.length} total)</span>
            </h2>
            
            {tasks.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <ClipboardList className="w-10 h-10 mx-auto mb-3 opacity-50" />
                <p>No tasks yet</p>
                <p className="text-sm mt-1">Tasks will appear here when synced</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`flex items-center gap-4 p-4 bg-[#1a1f26] rounded-xl border border-gray-800 hover:border-gray-700 transition-colors ${
                      task.status === 'completed' ? 'opacity-60' : ''
                    }`}
                  >
                    <button
                      onClick={() => toggleTaskStatus(task.id, task.status)}
                      className="flex-shrink-0"
                    >
                      {task.status === 'completed' ? (
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-500 hover:text-cyan-400" />
                      )}
                    </button>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className={`font-medium ${
                          task.status === 'completed' ? 'text-gray-400 line-through' : 'text-white'
                        }`}>
                          {task.title}
                        </h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                          {task.task_type}
                        </span>
                      </div>
                      <p className={`text-sm mt-1 ${getDueDateColor(task.due_at)}`}>
                        {formatDueDate(task.due_at)}
                      </p>
                    </div>
                    
                    {task.url && (
                      <a
                        href={task.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-400 hover:text-cyan-400 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar - Study Assistant */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-cyan-500/10 to-purple-500/10 rounded-2xl border border-cyan-500/20 p-5 h-[600px] flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Study Buddy</h2>
                <p className="text-xs text-gray-400">Ask me about {classData.code}</p>
              </div>
            </div>
            
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {chatMessages.length === 0 ? (
                <div className="text-center py-8">
                  <Bot className="w-12 h-12 mx-auto mb-3 text-cyan-400 opacity-50" />
                  <p className="text-gray-400 text-sm">Hi! I&apos;m your study buddy for {classData.code}.</p>
                  <p className="text-gray-500 text-xs mt-2">Ask me anything about the course!</p>
                  <div className="mt-4 space-y-2">
                    {[
                      `What's due soon in ${classData.code}?`,
                      `Explain the key concepts`,
                      `Help me study for the exam`,
                    ].map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => setChatInput(suggestion)}
                        className="block w-full text-left text-xs px-3 py-2 bg-gray-800/50 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors"
                      >
                        💡 {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] px-4 py-2 rounded-2xl text-sm ${
                        msg.role === 'user'
                          ? 'bg-cyan-500 text-white rounded-br-md'
                          : 'bg-gray-800 text-gray-200 rounded-bl-md'
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 text-gray-400 px-4 py-2 rounded-2xl rounded-bl-md text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            
            {/* Chat Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder={`Ask about ${classData.code}...`}
                className="flex-1 bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-2 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500"
              />
              <button
                onClick={handleSendMessage}
                disabled={chatLoading || !chatInput.trim()}
                className="p-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 rounded-xl transition-colors"
              >
                <Send className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
