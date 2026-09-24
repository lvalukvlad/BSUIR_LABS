const BASE = '/api'

async function req(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: opts.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (opts.raw) return res
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const d = data.detail
    let msg = 'ошибка сервера'
    if (Array.isArray(d)) {
      msg = d.map((x) => x.msg || JSON.stringify(x)).join('; ')
    } else if (d) {
      msg = d
    }
    throw new Error(msg)
  }
  return data
}

export const api = {
  documents: () => req('/documents'),
  document: (id) => req(`/documents/${id}`),
  upload: (form) => req('/documents/upload', { method: 'POST', body: form }),
  remove: (id) => req(`/documents/${id}`, { method: 'DELETE' }),
  metrics: () => req('/metrics'),
  exportMetrics: () => req('/metrics/export', { method: 'POST' }),
  help: () => req('/help'),
  exportUrl: (id) => `${BASE}/documents/${id}/export`,
}
