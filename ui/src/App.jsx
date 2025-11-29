import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';
import { Settings } from './components/Settings';
import { Moon, Sun } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('chat'); // chat, settings
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar 
        onSelectConversation={setCurrentConversationId}
        onNewChat={() => setCurrentConversationId(null)}
        onOpenSettings={() => setCurrentView('settings')}
        currentConversationId={currentConversationId}
      />
      
      <main className="flex-1 flex flex-col relative">
        <header className="h-14 border-b flex items-center justify-between px-4">
          <h1 className="font-semibold text-lg">
            {currentView === 'settings' ? 'Settings' : 'Chat'}
          </h1>
          <button 
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="p-2 rounded-full hover:bg-secondary transition-colors"
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </header>

        <div className="flex-1 overflow-hidden">
          {currentView === 'settings' ? (
            <Settings onBack={() => setCurrentView('chat')} />
          ) : (
            <Chat conversationId={currentConversationId} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
