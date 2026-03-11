import { useState, useEffect } from 'react';
import { api } from '../api';
import { ScrollText, Search, Filter, ChevronDown, ChevronUp, Clock, Coins } from 'lucide-react';

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [filterProvider, setFilterProvider] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  const pageSize = 15;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: pageSize };
      if (filterProvider) params.provider = filterProvider;
      if (filterStatus) params.status = filterStatus;
      const data = await api.getLogs(params);
      setLogs(data.logs);
      setTotal(data.total);
    } catch (e) {
      console.error('Failed to fetch logs:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page, filterProvider, filterStatus]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Request Logs</h1>
        <p>Complete audit trail of all AI requests routed through AegisNet</p>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 'var(--space-lg)', padding: 'var(--space-md) var(--space-lg)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center', flexWrap: 'wrap' }}>
          <Filter size={16} style={{ color: 'var(--color-text-muted)' }} />
          <select className="input" style={{ width: '180px' }} value={filterProvider} onChange={e => { setFilterProvider(e.target.value); setPage(1); }} id="log-filter-provider">
            <option value="">All Providers</option>
            <option value="local">Local</option>
          </select>
          <select className="input" style={{ width: '160px' }} value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setPage(1); }} id="log-filter-status">
            <option value="">All Status</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
          </select>
          <div style={{ marginLeft: 'auto', fontSize: 'var(--font-sm)', color: 'var(--color-text-muted)' }}>
            {total} total records
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-spinner" />
        ) : logs.length === 0 ? (
          <div className="empty-state">
            <ScrollText size={40} />
            <h3>No logs found</h3>
            <p>Requests will appear here once you start using the gateway</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Provider</th>
                    <th>Model</th>
                    <th>Strategy</th>
                    <th>Tokens</th>
                    <th>Cost</th>
                    <th>Latency</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(log => (
                    <>
                      <tr key={log.id} onClick={() => setExpandedId(expandedId === log.id ? null : log.id)} style={{ cursor: 'pointer' }}>
                        <td style={{ fontSize: 'var(--font-sm)' }}>{new Date(log.timestamp).toLocaleString()}</td>
                        <td><span className="badge neutral" style={{ textTransform: 'capitalize' }}>{log.provider}</span></td>
                        <td style={{ fontSize: 'var(--font-sm)', fontWeight: 500 }}>{log.model}</td>
                        <td style={{ fontSize: 'var(--font-sm)' }}>{log.routing_strategy}</td>
                        <td style={{ fontSize: 'var(--font-sm)' }}>{log.total_tokens}</td>
                        <td style={{ fontSize: 'var(--font-sm)', fontWeight: 500 }}>${log.cost_usd.toFixed(6)}</td>
                        <td style={{ fontSize: 'var(--font-sm)' }}>{log.latency_ms.toFixed(0)}ms</td>
                        <td><span className={`badge ${log.status === 'success' ? 'success' : 'error'}`}>{log.status}</span></td>
                        <td>{expandedId === log.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                      </tr>
                      {expandedId === log.id && (
                        <tr key={`${log.id}-expand`}>
                          <td colSpan={9} style={{ background: 'var(--color-bg)', padding: 'var(--space-lg)' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
                              <div>
                                <div style={{ fontWeight: 600, fontSize: 'var(--font-sm)', marginBottom: 'var(--space-sm)', color: 'var(--color-text-secondary)' }}>Prompt</div>
                                <div style={{ fontSize: 'var(--font-sm)', whiteSpace: 'pre-wrap', background: 'var(--color-surface)', padding: 'var(--space-md)', borderRadius: 'var(--radius-md)', maxHeight: '200px', overflow: 'auto' }}>
                                  {log.prompt}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontWeight: 600, fontSize: 'var(--font-sm)', marginBottom: 'var(--space-sm)', color: 'var(--color-text-secondary)' }}>Response</div>
                                <div style={{ fontSize: 'var(--font-sm)', whiteSpace: 'pre-wrap', background: 'var(--color-surface)', padding: 'var(--space-md)', borderRadius: 'var(--radius-md)', maxHeight: '200px', overflow: 'auto' }}>
                                  {log.response || '—'}
                                </div>
                              </div>
                            </div>
                            {log.error_message && (
                              <div style={{ marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: 'var(--color-danger-light)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-sm)', color: 'var(--color-danger)' }}>
                                {log.error_message}
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-sm)', padding: 'var(--space-md)', borderTop: '1px solid var(--color-border-light)' }}>
                <button className="btn btn-secondary btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</button>
                <span style={{ display: 'flex', alignItems: 'center', fontSize: 'var(--font-sm)', color: 'var(--color-text-secondary)', padding: '0 var(--space-md)' }}>
                  Page {page} of {totalPages}
                </span>
                <button className="btn btn-secondary btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
