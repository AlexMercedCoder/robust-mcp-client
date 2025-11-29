import React, { useState, useEffect } from 'react';
import { Save, ArrowLeft, Plus, Trash2 } from 'lucide-react';

export function Settings({ onBack }) {
  const [config, setConfig] = useState({
    provider: 'local',
    openai_key: '',
    gemini_key: '',
    anthropic_key: '',
    mcp_servers: []
  });
  const [status, setStatus] = useState('');
  const [newServer, setNewServer] = useState({ name: '', transport: 'stdio', command: '', args: '', url: '' });

  useEffect(() => {
    fetch('http://localhost:8000/api/config')
      .then(res => res.json())
      .then(data => {
        setConfig(prev => ({ ...prev, ...data }));
      })
      .catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          llm_provider: config.provider,
          openai_key: config.openai_key,
          gemini_key: config.gemini_key,
          anthropic_key: config.anthropic_key,
          mcp_servers: config.mcp_servers
        })
      });
      if (res.ok) {
        setStatus('Settings saved successfully!');
        setTimeout(() => setStatus(''), 3000);
      } else {
        setStatus('Failed to save settings.');
      }
    } catch (e) {
      setStatus('Error saving settings.');
    }
  };

  const addServer = () => {
    if (!newServer.name) return;
    const server = {
      name: newServer.name,
      transport: newServer.transport,
      command: newServer.transport === 'stdio' ? newServer.command : undefined,
      args: newServer.transport === 'stdio' ? newServer.args.split(' ').filter(Boolean) : [],
      url: newServer.transport === 'sse' ? newServer.url : undefined
    };
    setConfig(prev => ({ ...prev, mcp_servers: [...prev.mcp_servers, server] }));
    setNewServer({ name: '', transport: 'stdio', command: '', args: '', url: '' });
  };

  const removeServer = (idx) => {
    setConfig(prev => ({
      ...prev,
      mcp_servers: prev.mcp_servers.filter((_, i) => i !== idx)
    }));
  };

  return (
    <div className="p-6 max-w-2xl mx-auto h-full overflow-y-auto">
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft size={20} />
        Back to Chat
      </button>

      <h2 className="text-2xl font-bold mb-6">Settings</h2>

      <form onSubmit={handleSubmit} className="space-y-8 pb-10">
        <section className="space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2">LLM Configuration</h3>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Default LLM Provider</label>
            <select 
              value={config.provider}
              onChange={(e) => setConfig({...config, provider: e.target.value})}
              className="w-full p-2 rounded-md border bg-background"
            >
              <option value="local">Local (Llama.cpp)</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Google Gemini</option>
              <option value="anthropic">Anthropic Claude</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">OpenAI API Key</label>
            <input 
              type="password"
              value={config.openai_key}
              onChange={(e) => setConfig({...config, openai_key: e.target.value})}
              className="w-full p-2 rounded-md border bg-background"
              placeholder="sk-..."
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Gemini API Key</label>
            <input 
              type="password"
              value={config.gemini_key}
              onChange={(e) => setConfig({...config, gemini_key: e.target.value})}
              className="w-full p-2 rounded-md border bg-background"
              placeholder="AIza..."
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Anthropic API Key</label>
            <input 
              type="password"
              value={config.anthropic_key}
              onChange={(e) => setConfig({...config, anthropic_key: e.target.value})}
              className="w-full p-2 rounded-md border bg-background"
              placeholder="sk-ant-..."
            />
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2">MCP Servers</h3>
          
          <div className="space-y-4">
            {config.mcp_servers.map((server, idx) => (
              <div key={idx} className="flex items-start justify-between p-3 border rounded-md bg-secondary/20">
                <div>
                  <p className="font-medium">{server.name} <span className="text-xs bg-primary/10 text-primary px-1 rounded">{server.transport}</span></p>
                  {server.transport === 'stdio' ? (
                    <p className="text-sm text-muted-foreground font-mono">{server.command} {server.args.join(' ')}</p>
                  ) : (
                    <p className="text-sm text-muted-foreground font-mono">{server.url}</p>
                  )}
                </div>
                <button 
                  type="button"
                  onClick={() => removeServer(idx)}
                  className="text-destructive hover:text-destructive/80"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>

          <div className="border rounded-md p-4 space-y-3 bg-secondary/10">
            <h4 className="text-sm font-medium">Add New Server</h4>
            <div className="grid grid-cols-2 gap-2">
              <input 
                placeholder="Name"
                value={newServer.name}
                onChange={e => setNewServer({...newServer, name: e.target.value})}
                className="p-2 rounded-md border bg-background"
              />
              <select
                value={newServer.transport}
                onChange={e => setNewServer({...newServer, transport: e.target.value})}
                className="p-2 rounded-md border bg-background"
              >
                <option value="stdio">Stdio</option>
                <option value="sse">HTTP (SSE)</option>
              </select>
            </div>
            
            {newServer.transport === 'stdio' ? (
              <div className="space-y-2">
                <input 
                  placeholder="Command (e.g., npx)"
                  value={newServer.command}
                  onChange={e => setNewServer({...newServer, command: e.target.value})}
                  className="w-full p-2 rounded-md border bg-background"
                />
                <input 
                  placeholder="Args (space separated)"
                  value={newServer.args}
                  onChange={e => setNewServer({...newServer, args: e.target.value})}
                  className="w-full p-2 rounded-md border bg-background"
                />
              </div>
            ) : (
              <input 
                placeholder="URL (e.g., http://localhost:3000/sse)"
                value={newServer.url}
                onChange={e => setNewServer({...newServer, url: e.target.value})}
                className="w-full p-2 rounded-md border bg-background"
              />
            )}
            
            <button 
              type="button"
              onClick={addServer}
              className="w-full bg-secondary text-secondary-foreground py-2 rounded-md hover:bg-secondary/80 flex items-center justify-center gap-2"
            >
              <Plus size={16} /> Add Server
            </button>
          </div>
        </section>

        <button 
          type="submit"
          className="w-full bg-primary text-primary-foreground py-2 rounded-md hover:bg-primary/90 flex items-center justify-center gap-2"
        >
          <Save size={18} />
          Save Settings
        </button>

        {status && (
          <p className={`text-center text-sm ${status.includes('Error') || status.includes('Failed') ? 'text-destructive' : 'text-green-500'}`}>
            {status}
          </p>
        )}
      </form>
    </div>
  );
}
