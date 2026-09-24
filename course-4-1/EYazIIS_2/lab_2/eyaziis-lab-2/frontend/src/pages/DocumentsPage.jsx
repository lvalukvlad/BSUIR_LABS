import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { LanguageBadges, languagesFromDoc } from '../languages.jsx'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const reload = () => {
    Promise.all([api.documents(), api.stats()])
      .then(([docs, statistics]) => {
        setDocuments(docs.documents || [])
        setStats(statistics)
      })
      .catch((err) => setError(err.message))
  }

  useEffect(reload, [])

  const remove = async (id) => {
    if (!confirm(`Удалить документ №${id}?`)) return
    try {
      const result = await api.deleteDocument(id)
      setMessage(result.message)
      reload()
    } catch (err) {
      setError(err.message)
    }
  }

  const exportJson = async () => {
    try {
      const payload = await api.exportDocuments()
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'recognition-results.json'
      link.click()
      URL.revokeObjectURL(url)
      setMessage('Результаты сохранены в файл recognition-results.json')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      {stats && (
        <div className="stats" style={{ marginBottom: 16 }}>
          <div className="stat"><b>{stats.documents}</b><span>документов</span></div>
          <div className="stat"><b>{stats.results}</b><span>распознаваний</span></div>
          <div className="stat"><b>{stats.русский_count ?? 0}</b><span>русских</span></div>
          <div className="stat"><b>{stats.немецкий_count ?? 0}</b><span>немецких</span></div>
          <div className="stat"><b>{Number(stats.avg_doc_len || 0).toFixed(1)}</b><span>средняя длина</span></div>
        </div>
      )}

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      <div className="card no-print" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button type="button" className="secondary" onClick={exportJson}>Сохранить в файл</button>
        <button type="button" className="secondary" onClick={() => window.print()}>Печать</button>
      </div>

      <div className="card">
        <h2>Тестовая коллекция и загруженные документы</h2>
        <p className="muted">
          При запуске система сама распознаёт эталонные тексты из разметки оценки.
          PDF, загруженные на странице «Распознавание», попадают сюда отдельно.
        </p>
        {documents.length === 0 ? (
          <p className="muted">Нет документов. Загрузите PDF-файл на главной странице.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th className="num">№</th>
                <th>Название</th>
                <th>Источник</th>
                <th>Язык</th>
                <th className="num">Длина</th>
                <th>Дата</th>
                <th className="no-print"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td className="num">{doc.id}</td>
                  <td>
                    <Link to={`/documents/${doc.id}`}>{doc.title}</Link>
                    <div className="muted" style={{ fontSize: 13 }}>{doc.source_file || '—'}</div>
                  </td>
                  <td>
                    <span className={`source-badge ${doc.source_kind === 'etalon' ? 'source-etalon' : 'source-upload'}`}>
                      {doc.source_kind === 'etalon' ? 'эталон' : 'загрузка'}
                    </span>
                  </td>
                  <td>
                    <LanguageBadges {...languagesFromDoc(doc)} />
                  </td>
                  <td className="num">{doc.doc_len}</td>
                  <td>{doc.created_at || '—'}</td>
                  <td className="no-print">
                    <button className="danger" onClick={() => remove(doc.id)}>Удалить</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
