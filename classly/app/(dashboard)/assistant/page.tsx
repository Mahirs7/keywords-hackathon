'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  ChevronDown, 
  ChevronUp,
  Loader2,
  BookOpen,
  Sparkles,
  AlertCircle,
  Plus,
  X
} from 'lucide-react';

interface Course {
  id: string;
  code: string;
  title: string;
}

interface Source {
  title: string;
  source: string;
}

interface RetrievedChunk {
  chunk_id: string;
  doc_id: string;
  content: string;
  similarity: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  retrieved?: RetrievedChunk[];
  timestamp: Date;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function RAGAssistant() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourses, setSelectedCourses] = useState<string[]>([]);
  const [showCoursePicker, setShowCoursePicker] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const coursePickerRef = useRef<HTMLDivElement>(null);

  // Fetch available courses on mount
  useEffect(() => {
    fetchCourses();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Close course picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (coursePickerRef.current && !coursePickerRef.current.contains(event.target as Node)) {
        setShowCoursePicker(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleContextCourse = (courseCode: string) => {
    setSelectedCourses(prev => 
      prev.includes(courseCode) 
        ? prev.filter(c => c !== courseCode)
        : [...prev, courseCode]
    );
  };

  const removeContextCourse = (courseCode: string) => {
    setSelectedCourses(prev => prev.filter(c => c !== courseCode));
  };

  const fetchCourses = async () => {
    try {
      setLoadingCourses(true);
      const response = await fetch(`${API_BASE}/api/rag/courses`);
      const data = await response.json();
      
      if (data.success) {
        setCourses(data.courses);
      } else {
        setError('Failed to load courses');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.');
      console.error('Error fetching courses:', err);
    } finally {
      setLoadingCourses(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuestion('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/rag/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          courseCodes: selectedCourses,  // Empty array = all courses
          question: userMessage.content
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          retrieved: data.retrieved,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        setError(data.error || 'Failed to get answer');
      }
    } catch (err) {
      setError('Failed to get answer. Please try again.');
      console.error('Error asking question:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSources = (messageId: string) => {
    setExpandedSources(prev => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Course Assistant</h1>
            <p className="text-gray-400 text-sm">Ask questions about your course materials</p>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-[#0f1419] border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="w-16 h-16 text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-400 mb-2">
                Ask me anything about {selectedCourses.length > 0 ? selectedCourses.join(', ') : 'all your courses'}
              </h3>
              <p className="text-gray-500 text-sm max-w-md">
                I can help you find information about assignments, deadlines, 
                office hours, grading policies, and more from your course materials.
              </p>
              <div className="mt-6 flex flex-wrap gap-2 justify-center">
                {[
                  "What are the upcoming assignments?",
                  "When are office hours?",
                  "What's the grading policy?",
                  "When is the midterm?"
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setQuestion(suggestion)}
                    className="px-3 py-1.5 bg-purple-500/10 text-purple-400 rounded-full text-sm hover:bg-purple-500/20 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}
                
                <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                  <div
                    className={`rounded-xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-[#1a1f2e] text-gray-200'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                  
                  {/* Sources section for assistant messages */}
                  {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                    <div className="mt-2">
                      <button
                        onClick={() => toggleSources(message.id)}
                        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-300 transition-colors"
                      >
                        <BookOpen className="w-4 h-4" />
                        <span>{message.sources.length} source{message.sources.length > 1 ? 's' : ''}</span>
                        {expandedSources.has(message.id) ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                      
                      {expandedSources.has(message.id) && (
                        <div className="mt-2 space-y-2">
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="bg-[#1a1f2e]/50 border border-gray-800 rounded-lg px-3 py-2"
                            >
                              <p className="text-sm font-medium text-gray-300">{source.title}</p>
                              <p className="text-xs text-gray-500">{source.source}</p>
                            </div>
                          ))}
                          
                          {message.retrieved && message.retrieved.length > 0 && (
                            <div className="mt-3">
                              <p className="text-xs text-gray-500 mb-2">Retrieved chunks:</p>
                              {message.retrieved.map((chunk, idx) => (
                                <div
                                  key={idx}
                                  className="bg-[#0f1419] border border-gray-800 rounded-lg px-3 py-2 mb-2"
                                >
                                  <div className="flex justify-between items-center mb-1">
                                    <span className="text-xs text-gray-500">Chunk {idx + 1}</span>
                                    <span className="text-xs text-purple-400">
                                      {(chunk.similarity * 100).toFixed(1)}% match
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-400">{chunk.content}</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-cyan-500 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-[#1a1f2e] rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 text-gray-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching course materials...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mx-4 mb-2 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
          {/* Selected Course Pills */}
          <div className="flex flex-wrap gap-2 mb-3">
            {selectedCourses.length === 0 ? (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-500/20 text-gray-300 rounded-full text-xs">
                All Classes
              </span>
            ) : (
              selectedCourses.map(code => (
                <span
                  key={code}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs"
                >
                  {code}
                  <button
                    type="button"
                    onClick={() => removeContextCourse(code)}
                    className="hover:text-white"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))
            )}
          </div>
          
          <div className="flex gap-2">
            {/* Course Picker Button */}
            <div className="relative" ref={coursePickerRef}>
              <button
                type="button"
                onClick={() => setShowCoursePicker(!showCoursePicker)}
                className="h-full px-3 bg-[#1a1f2e] border border-gray-700 rounded-xl text-gray-400 hover:text-white hover:border-purple-500 transition-colors"
                title="Add course context"
              >
                <Plus className="w-5 h-5" />
              </button>
              
              {/* Course Picker Popup */}
              {showCoursePicker && courses.length > 0 && (
                <div className="absolute bottom-full left-0 mb-2 w-56 bg-[#1a1f2e] border border-gray-700 rounded-lg shadow-xl overflow-hidden z-10">
                  <div className="p-2 border-b border-gray-700">
                    <span className="text-xs text-gray-400">Filter by course</span>
                  </div>
                  <div className="max-h-48 overflow-y-auto">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedCourses([]);
                        setShowCoursePicker(false);
                      }}
                      className={`w-full px-3 py-2 text-left text-sm hover:bg-purple-500/20 transition-colors flex items-center justify-between ${
                        selectedCourses.length === 0 ? 'bg-purple-500/10 text-purple-300' : 'text-gray-300'
                      }`}
                    >
                      <span>All Classes</span>
                      {selectedCourses.length === 0 && (
                        <span className="text-purple-400">✓</span>
                      )}
                    </button>
                    {courses.map(course => (
                      <button
                        key={course.id}
                        type="button"
                        onClick={() => toggleContextCourse(course.code)}
                        className={`w-full px-3 py-2 text-left text-sm hover:bg-purple-500/20 transition-colors flex items-center justify-between ${
                          selectedCourses.includes(course.code) ? 'bg-purple-500/10 text-purple-300' : 'text-gray-300'
                        }`}
                      >
                        <span>{course.code} - {course.title}</span>
                        {selectedCourses.includes(course.code) && (
                          <span className="text-purple-400">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={`Ask about ${selectedCourses.length > 0 ? selectedCourses.join(', ') : 'your courses'}...`}
              disabled={isLoading}
              className="flex-1 bg-[#1a1f2e] border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="px-6 py-3 bg-linear-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
