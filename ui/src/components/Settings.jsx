import React, { useState, useEffect } from 'react';
import { Save, ArrowLeft } from 'lucide-react';

export function Settings({ onBack }) {
  const [config, setConfig] = useState({
    provider: 'local',
    openai_key: '',
    gemini_key: '',
    anthropic_key: '',
    mcp_servers: []
  });
  const [status, setStatus] = useState('');

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
          anthropic_key: config.anthropic_key
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

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft size={20} />
        Back to Chat
      </button>

      <h2 className="text-2xl font-bold mb-6">Settings</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
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

        <div className="space-y-2">
          <label className="block text-sm font-medium">Active MCP Servers</label>
          <div className="bg-secondary/50 p-4 rounded-md">
            {config.mcp_servers.length > 0 ? (
              <ul className="list-disc list-inside">
                {config.mcp_servers.map(s => <li key={s}>{s}</li>)}
              </ul>
            ) : (
              <p className="text-muted-foreground">No active servers</p>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              Edit <code>mcp.json</code> to add servers.
            </p>
          </div>
        </div>

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
