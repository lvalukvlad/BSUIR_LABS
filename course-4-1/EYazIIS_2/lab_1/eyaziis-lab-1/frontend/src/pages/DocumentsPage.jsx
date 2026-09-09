import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [stats, setStats] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const reload = () => {
    Promise.all([api.documents(), api.stats()])
      .then(([docs, statistics]) => {
        setDocuments(docs.documents)
        setStats(statistics)
      })
      .catch((err) => setError(err.message))
  }

  useEffect(reload, [])

  const remove = async (id) => {
    if (!confirm(`Удалить документ №${id} из индекса?`)) return
    try {
      const result = await api.deleteDocument(id)
      setMessage(result.message)
      reload()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      {stats && (
        <div className="stats" style={{ marginBottom: 16 }}>
          <div className="stat">
            <b>{stats.documents}</b>
            <span>документов</span>
          </div>
          <div className="stat">
            <b>{stats.terms}</b>
            <span>терминов в словаре</span>
          </div>
          <div className="stat">
            <b>{stats.postings}</b>
            <span>записей индекса</span>
          </div>
          <div className="stat">
            <b>{stats.avg_doc_len.toFixed(1)}</b>
            <span>средняя длина</span>
          </div>
          <div className="stat">
            <b>{stats.searches}</b>
            <span>запросов выполнено</span>
          </div>
        </div>
      )}

      {message && <div className="notice success">{message}</div>}
      {error && <div className="notice error">{error}</div>}

      <div className="card">
        <h2>Документы коллекции</h2>
        <table>
          <thead>
            <tr>
              <th className="num">№</th>
              <th>Заголовок</th>
              <th>Файл</th>
              <th className="num">Длина</th>
              <th>Дата</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td className="num">{doc.id}</td>
                <td>
                  <Link to={`/documents/${doc.id}`}>{doc.title}</Link>
                  <div className="muted" style={{ fontSize: 13 }}>
                    {doc.summary}
                  </div>
                </td>
                <td className="muted">{doc.source_file || '—'}</td>
                <td className="num">{doc.doc_len}</td>
                <td className="muted">{doc.created_at}</td>
                <td>
                  <button className="danger" onClick={() => remove(doc.id)}>
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
