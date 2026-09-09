const BASE = '/api'

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...options,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = payload.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
      : detail || 'Ошибка обращения к серверу'
    throw new Error(message)
  }
  return payload
}

export const api = {
  search: (body) => request('/search', { method: 'POST', body: JSON.stringify(body) }),
  suggest: (prefix) => request(`/suggest?prefix=${encodeURIComponent(prefix)}`),
  documents: () => request('/documents'),
  document: (id, query = '') => request(`/documents/${id}?query=${encodeURIComponent(query)}`),
  addDocument: (body) => request('/documents', { method: 'POST', body: JSON.stringify(body) }),
  uploadDocument: (formData) => request('/documents/upload', { method: 'POST', body: formData }),
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
  stats: () => request('/stats'),
  metrics: (topK) => request(`/metrics?top_k=${topK}`),
  exportMetrics: (topK) => request(`/metrics/export?top_k=${topK}`, { method: 'POST' }),
  help: () => request('/help'),
}
