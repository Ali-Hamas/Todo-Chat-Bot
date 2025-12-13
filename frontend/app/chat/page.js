'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { isAuthenticated, logoutUser } from '../../utils/auth';
import { useRouter } from 'next/navigation';

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
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <p className="text-lg text-gray-600 mb-4">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">Todo Assistant</h1>
          <div className="flex items-center space-x-4">
            {conversationId && (
              <span className="text-sm text-gray-500">
                Conversation: {conversationId}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="text-sm bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1 rounded-lg transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Welcome to Todo Assistant!</h2>
              <p className="text-gray-500">Ask me to manage your tasks:</p>
              <ul className="mt-4 space-y-2 text-sm text-gray-600">
                <li>"Add a task to buy groceries"</li>
                <li>"Show my pending tasks"</li>
                <li>"Mark task 1 as completed"</li>
              </ul>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 rounded-lg px-4 py-2 max-w-[80%]">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t py-4 px-6">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-500 text-white rounded-lg px-6 py-2 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Ask me to add, list, complete, or delete tasks
        </p>
      </div>
    </div>
  );
}