import { useState, useRef, useEffect } from 'react';
import { api } from '../api';
import { Send, Bot, User, Settings2, Loader2 } from 'lucide-react';
import './Playground.css';

export default function Playground() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('');
  const [strategy, setStrategy] = useState('auto');
  const [lastMeta, setLastMeta] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await api.chat({
        messages: newMessages.map(m => ({ role: m.role, content: m.content })),
        model: model || undefined,
        routing_strategy: strategy,
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.content }]);
      setLastMeta(res.metadata);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Playground</h1>
        <p>Test AI models through AegisNet's unified gateway</p>
      </div>

      <div className="playground-layout">
        {/* Chat Area */}
        <div className="chat-panel card">
          <div className="chat-messages" id="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <Bot size={48} />
                <h3>Welcome to AegisNet Playground</h3>
                <p>Send a message to test AI routing through the control plane.</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="chat-bubble">
                  <div className="chat-role">{msg.role === 'user' ? 'You' : 'AegisNet'}</div>
                  <div className="chat-content">{msg.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="chat-avatar"><Bot size={16} /></div>
                <div className="chat-bubble">
                  <Loader2 size={18} className="pulse" style={{ color: 'var(--color-primary)' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              className="input chat-input"
              placeholder="Type a message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              disabled={loading}
              id="chat-input"
            />
            <button className="btn btn-primary send-btn" onClick={sendMessage} disabled={loading} id="send-btn">
              <Send size={18} />
            </button>
          </div>
        </div>

        {/* Config Panel */}
        <div className="config-panel">
          <div className="card">
            <div className="card-header">
              <span className="card-title"><Settings2 size={16} /> Configuration</span>
            </div>

            <div className="config-field">
              <label>Routing Strategy</label>
              <select className="input" value={strategy} onChange={e => setStrategy(e.target.value)} id="strategy-select">
                <option value="auto">Auto (Smart)</option>
                <option value="cost_optimized">Cost Optimized</option>
                <option value="performance">Performance</option>
                <option value="quality">Quality</option>
              </select>
            </div>

            <div className="config-field">
              <label>Specific Model (optional)</label>
              <select className="input" value={model} onChange={e => setModel(e.target.value)} id="model-select">
                <option value="">Auto-select</option>
                <optgroup label="Local (Ollama)">
                  <option value="local/llama3">Llama 3</option>
                  <option value="local/llama3:8b">Llama 3 8B</option>
                  <option value="local/mistral">Mistral</option>
                  <option value="local/codellama">Code Llama</option>
                </optgroup>
              </select>
            </div>

            <button className="btn btn-secondary" style={{ width: '100%', marginTop: 'var(--space-md)', justifyContent: 'center' }}
              onClick={() => { setMessages([]); setLastMeta(null); }}>
              Clear Conversation
            </button>
          </div>

          {/* Response Metadata */}
          {lastMeta && (
            <div className="card" style={{ marginTop: 'var(--space-md)' }}>
              <div className="card-header">
                <span className="card-title">Last Response</span>
              </div>
              <div className="meta-grid">
                <div className="meta-item">
                  <span className="meta-label">Provider</span>
                  <span className="meta-value">{lastMeta.provider}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Model</span>
                  <span className="meta-value">{lastMeta.model}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Strategy</span>
                  <span className="meta-value">{lastMeta.routing_strategy}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Latency</span>
                  <span className="meta-value">{lastMeta.latency_ms.toFixed(0)} ms</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Tokens</span>
                  <span className="meta-value">{lastMeta.total_tokens}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Cost</span>
                  <span className="meta-value">${lastMeta.cost_usd.toFixed(6)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
