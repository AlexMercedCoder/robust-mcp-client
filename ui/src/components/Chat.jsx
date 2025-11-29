import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Send, StopCircle, Download } from 'lucide-react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false });

const Mermaid = ({ chart }) => {
  const ref = useRef(null);
  const [svg, setSvg] = useState('');

  useEffect(() => {
    if (chart && ref.current) {
      mermaid.render(`mermaid-${Date.now()}`, chart).then(({ svg }) => {
        setSvg(svg);
      }).catch((e) => {
        console.error("Mermaid error", e);
        setSvg(`<pre class="text-red-500">Error rendering chart</pre>`);
      });
    }
  }, [chart]);

  return (
    <div className="my-4 bg-white p-4 rounded-md overflow-x-auto" dangerouslySetInnerHTML={{ __html: svg }} />
  );
};

const CodeBlock = ({ language, children }) => {
  if (language === 'mermaid') {
    return <Mermaid chart={children} />;
  }
  return (
    <SyntaxHighlighter
      style={vscDarkPlus}
      language={language}
      PreTag="div"
      className="rounded-md my-2"
    >
      {String(children).replace(/\n$/, '')}
    </SyntaxHighlighter>
  );
};

export function Chat({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (conversationId) {
      fetchHistory(conversationId);
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/api/history/${id}`);
      const data = await res.json();
      setMessages(data);
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    let currentConvId = conversationId;
    if (!currentConvId) {
      // Create new conversation first
      try {
        const res = await fetch('http://localhost:8000/api/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: input.substring(0, 30) })
        });
        const data = await res.json();
        currentConvId = data.id;
        // Ideally notify parent to update sidebar selection, but for now we just proceed
      } catch (e) {
        console.error("Failed to create conversation", e);
        setIsLoading(false);
        return;
      }
    }

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content, conversation_id: currentConvId }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: 'assistant', content: '' };
      
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        assistantMsg.content += chunk;
        
        setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = { ...assistantMsg };
          return newMsgs;
        });
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error('Error:', error);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-4 ${
              msg.role === 'user' 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-card border shadow-sm'
            }`}>
              <ReactMarkdown
                components={{
                  code({node, inline, className, children, ...props}) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <CodeBlock language={match[1]}>{String(children).replace(/\n$/, '')}</CodeBlock>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t bg-background">
        <form onSubmit={sendMessage} className="flex gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-secondary text-foreground rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
          {isLoading ? (
            <button 
              type="button" 
              onClick={stopGeneration}
              className="bg-destructive text-destructive-foreground p-2 rounded-md hover:bg-destructive/90"
            >
              <StopCircle size={20} />
            </button>
          ) : (
            <button 
              type="submit" 
              disabled={!input.trim()}
              className="bg-primary text-primary-foreground p-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          )}
        </form>
      </div>
    </div>
  );
}
