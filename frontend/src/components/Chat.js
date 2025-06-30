import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import ChatSidebar from './ChatSidebar';
import ChatMessages from './ChatMessages';
import DocumentUpload from './DocumentUpload';
import { MessageSquare, Upload, LogOut, Menu, X, Send, Settings } from 'lucide-react';
import api from '../utils/axios';
import { v4 as uuidv4 } from 'uuid';

function Chat() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const getErrorMessage = (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      return 'Unable to connect to the server. Please check your connection and try again.';
    }
    
    if (error.response?.status === 500) {
      return 'Server error. Please try again later.';
    }
    
    if (error.response?.status === 401) {
      return 'Authentication failed. Please log in again.';
    }
    
    return 'An unexpected error occurred. Please try again.';
  };

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      setError('');
      const response = await api.get('/chat/history');
      setChats(response.data.chats);
    } catch (error) {
      console.error('Error loading chat history:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      
      // If authentication failed, redirect to login
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const loadChatMessages = async (chatId) => {
    try {
      setError('');
      const response = await api.get(`/chat/${chatId}/messages`);
      setMessages(response.data.messages);
      setCurrentChat(chatId);
    } catch (error) {
      console.error('Error loading chat messages:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      
      // If authentication failed, redirect to login
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    setLoading(true);
    setError('');

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    // Use a unique ID for the assistant message to update it correctly
    const assistantMessageId = uuidv4();
    const assistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    try {
      const formData = new FormData();
      formData.append('message', message);
      if (currentChat) {
        formData.append('chat_id', currentChat);
      }

      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last line in buffer if it's incomplete
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);

              if (firstChunk) {
                if (data.chat_id && !currentChat) {
                  setCurrentChat(data.chat_id);
                  loadChatHistory();
                }
                firstChunk = false;
              } else if (data.response) {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: msg.content + data.response }
                      : msg
                  )
                );
                // Small delay to make streaming visible
                await new Promise(resolve => setTimeout(resolve, 10));
              }
            } catch (error) {
              console.warn('Failed to parse JSON line:', line, error);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Sorry, I encountered an error. Please try again.' }
            : msg
        )
      );

      if (error.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = async (chatId) => {
    try {
      setError('');
      await api.delete(`/chat/${chatId}`);
      await loadChatHistory();
      
      if (currentChat === chatId) {
        setCurrentChat(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      
      // If authentication failed, redirect to login
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)}></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <ChatSidebar
          chats={chats}
          currentChat={currentChat}
          onChatSelect={loadChatMessages}
          onDeleteChat={deleteChat}
          onNewChat={() => {
            const newChatId = uuidv4();
            setCurrentChat(newChatId);
            setMessages([]);
            setSidebarOpen(false);
            setError('');
            setChats(prev => [{ id: newChatId, title: 'New Chat', created_at: new Date().toISOString() }, ...prev]);
          }}
        />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-gray-900">RAG Chatbot</h1>
              <p className="text-sm text-gray-500">Welcome, {user?.username}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {user?.is_admin && (
              <button
                onClick={() => navigate('/admin')}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                title="Admin Dashboard"
              >
                <Settings className="h-5 w-5" />
              </button>
            )}
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError('')}
                  className="inline-flex text-red-400 hover:text-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Chat messages */}
        <div className="flex-1 overflow-hidden">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No messages yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Start a conversation by typing a message below.
                </p>
              </div>
            </div>
          ) : (
            <ChatMessages
              messages={messages}
              loading={loading}
              messagesEndRef={messagesEndRef}
            />
          )}
        </div>

        {/* Input form - always visible */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={(e) => {
            e.preventDefault();
            const input = e.target.querySelector('input[type="text"]');
            if (input && input.value.trim() && !loading) {
              sendMessage(input.value);
              input.value = '';
            }
          }} className="flex space-x-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Type your message..."
                disabled={loading}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Document upload modal - only for admins */}
      {user?.is_admin && showUpload && (
        <DocumentUpload
          onClose={() => setShowUpload(false)}
          onUploadSuccess={() => {
            setShowUpload(false);
            setError('');
          }}
        />
      )}
    </div>
  );
}

export default Chat; 