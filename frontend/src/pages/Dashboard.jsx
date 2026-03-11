import { useState, useEffect } from 'react';
import { api } from '../api';
import {
  Activity, DollarSign, Zap, Server,
  ArrowUpRight, Clock
} from 'lucide-react';

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [models, setModels] = useState(null);
  const [recentLogs, setRecentLogs] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [analyticsData, modelsData, logsData] = await Promise.allSettled([
          api.getAnalytics(),
          api.getModels(),
          api.getLogs({ page_size: 5 }),
        ]);
        if (analyticsData.status === 'fulfilled') setAnalytics(analyticsData.value);
        if (modelsData.status === 'fulfilled') setModels(modelsData.value);
        if (logsData.status === 'fulfilled') setRecentLogs(logsData.value);
      } catch (e) {
        console.error('Dashboard fetch error:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading-spinner" />;

  const stats = analytics || {};

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of your AI control plane</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon red">
            <Activity size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Total Requests</div>
            <div className="stat-value">{(stats.total_requests || 0).toLocaleString()}</div>
            <div className="stat-trend">All time</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <DollarSign size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Total Cost</div>
            <div className="stat-value">${(stats.total_cost_usd || 0).toFixed(4)}</div>
            <div className="stat-trend">USD</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            <Zap size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Avg Latency</div>
            <div className="stat-value">{(stats.avg_latency_ms || 0).toFixed(0)} ms</div>
            <div className="stat-trend">Per request</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon yellow">
            <Server size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Active Models</div>
            <div className="stat-value">{models?.providers?.filter(p => p.status === 'healthy').length || 0}</div>
            <div className="stat-trend">of {models?.providers?.length || 0} connected</div>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Model Status */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Provider Status</span>
          </div>
          {models?.providers?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {models.providers.map(p => (
                <div key={p.provider} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)'
                }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{p.display_name}</div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>
                      {p.models_available?.length || 0} models
                    </div>
                  </div>
                  <span className={`badge ${p.status === 'healthy' ? 'success' : p.status === 'down' ? 'error' : 'warning'}`}>
                    {p.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <Server size={32} />
              <h3>No providers connected</h3>
              <p>Configure API keys in .env to get started</p>
            </div>
          )}
        </div>

        {/* Recent Requests */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Requests</span>
          </div>
          {recentLogs?.logs?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recentLogs.logs.map(log => (
                <div key={log.id} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 16px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)'
                }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 500, fontSize: 'var(--font-sm)',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px'
                    }}>
                      {log.prompt}
                    </div>
                    <div style={{
                      display: 'flex', gap: 'var(--space-md)',
                      fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', marginTop: '2px'
                    }}>
                      <span>{log.model}</span>
                      <span><Clock size={10} /> {log.latency_ms.toFixed(0)}ms</span>
                    </div>
                  </div>
                  <span className={`badge ${log.status === 'success' ? 'success' : 'error'}`}>
                    {log.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <Activity size={32} />
              <h3>No requests yet</h3>
              <p>Send your first request via the Playground</p>
            </div>
          )}
        </div>
      </div>

      {/* Usage by Provider */}
      {stats.requests_by_provider && Object.keys(stats.requests_by_provider).length > 0 && (
        <div className="card" style={{ marginTop: 'var(--space-lg)' }}>
          <div className="card-header">
            <span className="card-title">Usage by Provider</span>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-lg)', flexWrap: 'wrap' }}>
            {Object.entries(stats.requests_by_provider).map(([provider, count]) => (
              <div key={provider} style={{
                flex: '1 1 200px', padding: '16px',
                background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', textAlign: 'center'
              }}>
                <div style={{ fontSize: 'var(--font-xl)', fontWeight: 700 }}>{count}</div>
                <div style={{ fontSize: 'var(--font-sm)', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                  {provider}
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-primary)', marginTop: '4px' }}>
                  ${(stats.cost_by_provider?.[provider] || 0).toFixed(4)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
