'use client';

import { Bot, Send } from 'lucide-react';
import { useState } from 'react';

export default function AIAssistant() {
  const [message, setMessage] = useState('');

  return (
    <div className="bg-[#0f1419] rounded-2xl border border-gray-800">
      <div className="flex items-center gap-3 p-5 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
      </div>
      <div className="p-5">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-white mb-1">Study Assistant</p>
            <p className="text-sm text-gray-400">
              I can help you plan your study sessions, summarize materials, or answer questions about your coursework.
            </p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="space-y-2 mb-4">
          <button className="w-full text-left px-4 py-3 bg-[#1a1f26] rounded-xl text-sm text-gray-300 hover:bg-gray-800 transition-colors">
            📚 Help me study for my CS 101 exam
          </button>
          <button className="w-full text-left px-4 py-3 bg-[#1a1f26] rounded-xl text-sm text-gray-300 hover:bg-gray-800 transition-colors">
            📝 Summarize this week&apos;s readings
          </button>
          <button className="w-full text-left px-4 py-3 bg-[#1a1f26] rounded-xl text-sm text-gray-300 hover:bg-gray-800 transition-colors">
            🗓️ Create a study plan for midterms
          </button>
        </div>

        {/* Input */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 bg-[#1a1f26] border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <button className="p-3 bg-cyan-500 rounded-xl text-white hover:bg-cyan-600 transition-colors">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
