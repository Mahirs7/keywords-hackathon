'use client';

import { useState, useRef, useEffect } from 'react';
import { Bot, Send, Loader2, Calendar, CheckCircle, XCircle } from 'lucide-react';
import Header from '../components/Header';
import { mockUser, getGreeting, getFormattedDate } from '../lib/mockData';
import { createClient } from '../lib/supabase/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function AIPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI study assistant. I can help you check assignments, create calendar events, and plan your study schedule. What would you like to do?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [checkingCalendar, setCheckingCalendar] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Get user session and token
    const getSession = async () => {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        setUserToken(session.access_token);
      }
    };
    getSession();
  }, []);

  useEffect(() => {
    // Check calendar connection status on mount (after token is available)
    if (userToken) {
      checkCalendarStatus();
    }
    
    // Check URL params for OAuth callback
    const params = new URLSearchParams(window.location.search);
    if (params.get('calendar_connected') === 'true') {
      setCalendarConnected(true);
      // Clean URL
      window.history.replaceState({}, '', '/ai');
    } else if (params.get('calendar_error')) {
      const error = params.get('calendar_error');
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Error connecting Google Calendar: ${error}. Please try again.`,
        timestamp: new Date(),
      }]);
      window.history.replaceState({}, '', '/ai');
    }
  }, [userToken]);

  const checkCalendarStatus = async () => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (userToken) {
        headers['Authorization'] = `Bearer ${userToken}`;
      }
      
      const response = await fetch('http://localhost:5000/api/calendar/oauth/status', {
        headers,
      });
      const data = await response.json();
      setCalendarConnected(data.connected || false);
    } catch (error) {
      console.error('Error checking calendar status:', error);
    } finally {
      setCheckingCalendar(false);
    }
  };

  const handleConnectCalendar = async () => {
    if (!userToken) {
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Please log in first to connect your Google Calendar.',
        timestamp: new Date(),
      }]);
      return;
    }
    
    try {
      // Get OAuth URL from backend with Authorization header
      const response = await fetch('http://localhost:5000/api/calendar/oauth/authorize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to get OAuth URL');
      }
      
      const data = await response.json();
      if (data.success && data.auth_url) {
        // Redirect to Google OAuth consent screen
        window.location.href = data.auth_url;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error: any) {
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Error connecting Google Calendar: ${error.message || 'Unknown error'}`,
        timestamp: new Date(),
      }]);
    }
  };

  const handleDisconnectCalendar = async () => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (userToken) {
        headers['Authorization'] = `Bearer ${userToken}`;
      }
      
      const response = await fetch('http://localhost:5000/api/calendar/oauth/disconnect', {
        method: 'POST',
        headers,
      });
      const data = await response.json();
      if (data.success) {
        setCalendarConnected(false);
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: '✅ Google Calendar disconnected successfully.',
          timestamp: new Date(),
        }]);
      }
    } catch (error) {
      console.error('Error disconnecting calendar:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (userToken) {
        headers['Authorization'] = `Bearer ${userToken}`;
      }
      
      const response = await fetch('http://localhost:5000/api/ai/chat', {
        method: 'POST',
        headers,
        body: JSON.stringify({ message: input.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
          throw new Error(errorData.error || 'Authentication required. Please log in.');
        }
        throw new Error(errorData.error || 'Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I apologize, but I encountered an error processing your request.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running and try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <Header 
        greeting={getGreeting()} 
        userName={mockUser.name} 
        date={getFormattedDate()} 
      />

      <div className="bg-[#0f1419] rounded-2xl border border-gray-800 flex flex-col h-[calc(100vh-12rem)]">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">AI Study Assistant</h2>
              <p className="text-sm text-gray-400">Powered by Keywords AI</p>
            </div>
          </div>
          
          {/* Calendar Connection Status */}
          <div className="flex items-center gap-2">
            {checkingCalendar ? (
              <div className="flex items-center gap-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Checking...</span>
              </div>
            ) : calendarConnected ? (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-green-400">Calendar Connected</span>
                </div>
                <button
                  onClick={handleDisconnectCalendar}
                  className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <button
                onClick={handleConnectCalendar}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400 hover:bg-blue-500/20 transition-colors"
              >
                <Calendar className="w-4 h-4" />
                <span className="text-sm font-medium">Connect Calendar</span>
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-cyan-500 text-white'
                    : 'bg-[#1a1f26] text-gray-100 border border-gray-700'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {message.timestamp.toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                  })}
                </p>
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm text-gray-300">
                    {mockUser.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-[#1a1f26] border border-gray-700 rounded-2xl px-4 py-3">
                <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-5 border-t border-gray-800">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything... (e.g., 'Check for pending assignments this week and create a calendar entry')"
              className="flex-1 bg-[#1a1f26] border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="p-3 bg-cyan-500 rounded-xl text-white hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 px-1">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}

