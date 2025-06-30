import React from 'react';
import { MessageSquare, Plus, Trash2, Calendar } from 'lucide-react';

function ChatSidebar({ chats, currentChat, onChatSelect, onDeleteChat, onNewChat }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </button>
      </div>

      {/* Chat list */}
      <div className="flex-1 overflow-y-auto">
        {chats.length === 0 ? (
          <div className="p-4 text-center">
            <MessageSquare className="mx-auto h-8 w-8 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">No conversations yet</p>
            <p className="text-xs text-gray-400">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="p-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`group relative flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer transition-colors ${
                  currentChat === chat.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
                onClick={() => onChatSelect(chat.id)}
              >
                <MessageSquare className="h-4 w-4 mr-3 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="truncate">{chat.title}</p>
                  <div className="flex items-center text-xs text-gray-400 mt-1">
                    <Calendar className="h-3 w-3 mr-1" />
                    {formatDate(chat.created_at)}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-600 transition-opacity"
                  title="Delete chat"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          <p>Offline RAG Chatbot</p>
          <p>Powered by Ollama & Local Models</p>
        </div>
      </div>
    </div>
  );
}

export default ChatSidebar; 