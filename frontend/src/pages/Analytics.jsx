import { useState, useEffect } from 'react';
import { api } from '../api';
import { BarChart3, TrendingUp } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend
} from 'recharts';

const COLORS = ['#E53E3E', '#3182CE', '#38A169', '#D69E2E', '#805AD5', '#DD6B20'];

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetch() {
      try {
        const res = await api.getAnalytics();
        setData(res);
      } catch (e) {
        console.error('Analytics error:', e);
      } finally {
        setLoading(false);
      }
    }
    fetch();
    const interval = setInterval(fetch, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading-spinner" />;

  if (!data || data.total_requests === 0) {
    return (
      <div className="fade-in">
        <div className="page-header">
          <h1>Analytics</h1>
          <p>Insights into cost, performance, and usage across all AI providers</p>
        </div>
        <div className="card">
          <div className="empty-state">
            <BarChart3 size={40} />
            <h3>No data yet</h3>
            <p>Analytics will populate as requests flow through the gateway</p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const providerData = Object.entries(data.requests_by_provider || {}).map(([name, count]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    requests: count,
    cost: data.cost_by_provider?.[name] || 0,
  }));

  const modelData = Object.entries(data.requests_by_model || {}).map(([name, count]) => ({
    name, count,
  }));

  const latencyData = (data.recent_latency || []).map((v, i) => ({
    request: i + 1,
    latency: Math.round(v),
  }));

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Insights into cost, performance, and usage across all AI providers</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-info">
            <div className="stat-label">Total Requests</div>
            <div className="stat-value">{data.total_requests.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-info">
            <div className="stat-label">Total Tokens</div>
            <div className="stat-value">{data.total_tokens.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-info">
            <div className="stat-label">Total Cost</div>
            <div className="stat-value">${data.total_cost_usd.toFixed(4)}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-info">
            <div className="stat-label">Success Rate</div>
            <div className="stat-value">{data.success_rate.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Requests by Provider */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Requests by Provider</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer>
              <BarChart data={providerData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0E0E0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    background: 'white', border: '1px solid #F0E0E0',
                    borderRadius: '8px', fontSize: '13px'
                  }}
                />
                <Bar dataKey="requests" fill="#E53E3E" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Distribution */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Model Distribution</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={modelData}
                  dataKey="count"
                  nameKey="name"
                  cx="50%" cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {modelData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cost by Provider */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Cost by Provider</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer>
              <BarChart data={providerData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0E0E0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `$${v.toFixed(4)}`} />
                <Tooltip
                  contentStyle={{
                    background: 'white', border: '1px solid #F0E0E0',
                    borderRadius: '8px', fontSize: '13px'
                  }}
                  formatter={v => `$${v.toFixed(6)}`}
                />
                <Bar dataKey="cost" fill="#38A169" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Latency Trend */}
        {latencyData.length > 0 && (
          <div className="card">
            <div className="card-header">
              <span className="card-title">Latency Trend</span>
            </div>
            <div className="chart-container">
              <ResponsiveContainer>
                <LineChart data={latencyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F0E0E0" />
                  <XAxis dataKey="request" tick={{ fontSize: 12 }} label={{ value: 'Request #', position: 'bottom', fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} label={{ value: 'ms', angle: -90, position: 'insideLeft', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      background: 'white', border: '1px solid #F0E0E0',
                      borderRadius: '8px', fontSize: '13px'
                    }}
                    formatter={v => `${v} ms`}
                  />
                  <Line type="monotone" dataKey="latency" stroke="#E53E3E" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
