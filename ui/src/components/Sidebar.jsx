import React, { useEffect, useState } from 'react';
import { Plus, MessageSquare, Settings as SettingsIcon, Trash2 } from 'lucide-react';
import { clsx } from 'clsx';

export function Sidebar({ onSelectConversation, onNewChat, onOpenSettings, currentConversationId }) {
  const [conversations, setConversations] = useState([]);

  const fetchConversations = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/conversations');
      const data = await res.json();
      setConversations(data);
    } catch (e) {
      console.error("Failed to fetch conversations", e);
    }
  };

  useEffect(() => {
    fetchConversations();
    // Poll for updates or use context/event bus in real app
    const interval = setInterval(fetchConversations, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-64 border-r bg-secondary/30 flex flex-col">
      <div className="p-4">
        <button 
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 transition-colors"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelectConversation(conv.id)}
            className={clsx(
              "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              currentConversationId === conv.id 
                ? "bg-secondary text-secondary-foreground" 
                : "hover:bg-secondary/50 text-muted-foreground hover:text-foreground"
            )}
          >
            <MessageSquare size={16} />
            <span className="truncate text-left flex-1">{conv.title}</span>
          </button>
        ))}
      </div>

      <div className="p-4 border-t">
        <button 
          onClick={onOpenSettings}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors"
        >
          <SettingsIcon size={18} />
          Settings
        </button>
      </div>
    </aside>
  );
}
