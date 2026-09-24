const BASE = '/api'

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...options,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || 'Ошибка обращения к серверу')
  }
  return payload
}

export const api = {
  health: () => request('/health'),
  recognize: (formData) => request('/recognize', { method: 'POST', body: formData }),
  documents: () => request('/documents'),
  document: (id) => request(`/documents/${id}`),
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
  exportDocuments: () => request('/documents/export'),
  stats: () => request('/stats'),
  metrics: () => request('/metrics'),
  exportMetrics: () => request('/metrics/export', { method: 'POST' }),
  help: () => request('/help'),
  initDb: (force) => request(`/init-db?force=${force}`, { method: 'POST' }),
}
