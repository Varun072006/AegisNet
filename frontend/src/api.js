const API_BASE = 'http://localhost:8001/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };
  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Health
  health: () => request('/health'),

  // Chat
  chat: (data) => request('/chat', { method: 'POST', body: JSON.stringify(data) }),

  // Models
  getModels: () => request('/models'),

  // Logs
  getLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/logs${query ? '?' + query : ''}`);
  },

  // Analytics
  getAnalytics: () => request('/analytics'),
};
