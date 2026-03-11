import { useState, useEffect } from 'react';
import { api } from '../api';
import { Server, CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function Models() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const data = await api.getModels();
      setProviders(data.providers);
    } catch (e) {
      console.error('Failed to fetch models:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchModels(); }, []);

  const statusIcon = (status) => {
    if (status === 'healthy') return <CheckCircle2 size={18} style={{ color: 'var(--color-success)' }} />;
    if (status === 'down') return <XCircle size={18} style={{ color: 'var(--color-danger)' }} />;
    return <AlertCircle size={18} style={{ color: 'var(--color-warning)' }} />;
  };

  const providerColors = {
    local: '#6366F1',
  };

  return (
    <div className="fade-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Models</h1>
          <p>Connected AI providers and their available models</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchModels} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'pulse' : ''} /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading-spinner" />
      ) : providers.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Server size={40} />
            <h3>No providers configured</h3>
            <p>Add API keys to your .env file to connect providers</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 'var(--space-lg)' }}>
          {providers.map(p => (
            <div key={p.provider} className="card" style={{ position: 'relative', overflow: 'hidden' }}>
              {/* Accent bar */}
              <div style={{
                position: 'absolute', top: 0, left: 0, right: 0, height: '3px',
                background: providerColors[p.provider] || 'var(--color-primary)',
              }} />

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 'var(--radius-md)',
                    background: `${providerColors[p.provider]}15`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: providerColors[p.provider],
                    fontWeight: 700, fontSize: 'var(--font-lg)',
                  }}>
                    {p.display_name.charAt(0)}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 'var(--font-md)' }}>{p.display_name}</div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>{p.provider}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                  {statusIcon(p.status)}
                  <span className={`badge ${p.status === 'healthy' ? 'success' : p.status === 'down' ? 'error' : 'warning'}`}>
                    {p.status}
                  </span>
                </div>
              </div>

              {/* Models list */}
              <div style={{ fontWeight: 600, fontSize: 'var(--font-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-sm)' }}>
                Available Models
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: 'var(--space-md)' }}>
                {p.models_available?.map(m => (
                  <span key={m} className="badge neutral" style={{ fontSize: '11px' }}>{m}</span>
                ))}
              </div>

              {/* Pricing */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)', marginTop: 'auto' }}>
                <div style={{ padding: '10px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>Input/1K</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 600 }}>${p.cost_per_1k_input.toFixed(4)}</div>
                </div>
                <div style={{ padding: '10px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>Output/1K</div>
                  <div style={{ fontSize: 'var(--font-sm)', fontWeight: 600 }}>${p.cost_per_1k_output.toFixed(4)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
