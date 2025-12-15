'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { isAuthenticated, logoutUser } from '../../utils/auth';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';

export default function ChatPage() {
  const { messages, sendMessage, isLoading, conversationId, clearConversation } = useChat();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const router = useRouter();

  // Check authentication on component mount
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    await sendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleLogout = () => {
    logoutUser();
    router.push('/login');
  };

  if (!isAuthenticated()) {
    return (
      <div className="flex items-center justify-center min-h-screen text-white">
        <div className="text-center">
          <p className="text-lg text-gray-400 mb-4">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden relative">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/20 blur-[120px]" />
      </div>

      {/* Header */}
      <header className="glass border-b border-white/10 py-4 px-6 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <span className="text-white text-lg font-bold">A</span>
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Todo Assistant</h1>
          </div>
          <div className="flex items-center space-x-4">
            {conversationId && (
              <span className="text-xs text-gray-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                ID: {conversationId}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="text-sm bg-red-500/10 hover:bg-red-500/20 text-red-400 px-4 py-2 rounded-lg transition-all border border-red-500/20"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 scroll-smooth">
        <div className="max-w-4xl mx-auto space-y-6">
          <AnimatePresence mode="popLayout">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-20"
              >
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-2xl mx-auto flex items-center justify-center mb-6 border border-white/10 backdrop-blur-sm">
                  <span className="text-4xl">👋</span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-3">Welcome to Todo Assistant!</h2>
                <p className="text-gray-400 mb-8 max-w-md mx-auto">
                  I can help you manage your tasks efficiently. Just tell me what you need to do.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left max-w-3xl mx-auto text-sm">
                  {['Add a task to buy milk', 'Show my pending tasks', 'Mark task 1 as done'].map((cmd, i) => (
                    <button
                      key={i}
                      onClick={() => setInputValue(cmd)}
                      className="glass p-4 rounded-xl hover:bg-white/10 transition-colors cursor-pointer border border-white/5 group"
                    >
                      <span className="text-purple-400 group-hover:text-purple-300 transition-colors">Example: </span>
                      <span className="text-gray-300 block mt-1">"{cmd}"</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            ) : (
              messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, scale: 0.95, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-6 py-4 shadow-lg backdrop-blur-md border ${message.role === 'user'
                        ? 'bg-blue-600/80 text-white border-blue-500/30 rounded-br-sm'
                        : 'bg-white/10 text-gray-100 border-white/10 rounded-bl-sm'
                      }`}
                  >
                    <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="glass px-6 py-4 rounded-2xl rounded-bl-sm border border-white/10">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="glass border-t border-white/10 py-6 px-6 z-10">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex gap-3 relative">
            <input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all shadow-inner"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl px-8 py-2 font-semibold hover:shadow-lg hover:shadow-purple-500/20 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              Send
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-3 text-center">
            AI can make mistakes. Please verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}