import { useState } from 'react';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);

  // Helper function to get auth token from localStorage
  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      content: messageText,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Get auth token
      const token = getAuthToken();

      if (!token) {
        throw new Error('No authentication token found. Please log in first.');
      }

      // Use the same API base URL pattern as auth functions
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

      // Send message to backend API with authorization
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: messageText,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('Error parsing JSON response:', parseError);
        throw new Error('Invalid response format from server');
      }

      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      if (data.response) {
        const botMessage = {
          id: Date.now() + 1,
          content: data.response,
          role: 'assistant',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          content: data.error || 'Sorry, I encountered an error processing your request.',
          role: 'assistant',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        content: error.message || 'Sorry, I encountered an error connecting to the server. Please make sure you are logged in.',
        role: 'assistant',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  return {
    messages,
    sendMessage,
    isLoading,
    conversationId,
    clearConversation
  };
};