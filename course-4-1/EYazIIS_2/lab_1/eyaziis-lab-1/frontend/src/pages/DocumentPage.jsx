import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api.js'

export default function DocumentPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const [document, setDocument] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .document(id, query)
      .then(setDocument)
      .catch((err) => setError(err.message))
  }, [id, query])

  if (error) return <div className="notice error">{error}</div>
  if (!document) return <div className="card">Загрузка документа...</div>

  return (
    <>
      <div className="card">
        <h2>{document.title}</h2>
        <div className="meta">
          <span>Идентификатор: {document.id}</span>
          <span>Дата добавления: {document.created_at}</span>
          <span>Длина: {document.doc_len} терминов</span>
          {document.source_file && <span>Файл: {document.source_file}</span>}
        </div>

        {document.key_terms?.length > 0 && (
          <>
            <h3>Поисковый образ документа (ключевые термины)</h3>
            <div className="chips">
              {document.key_terms.map((term) => (
                <span className="chip" key={term.term}>
                  {term.term} · {Number(term.weight).toFixed(2)}
                </span>
              ))}
            </div>
          </>
        )}

        <div className="doc-text" dangerouslySetInnerHTML={{ __html: document.highlighted }} />
      </div>

      <Link to="/documents">← К списку документов</Link>
    </>
  )
}
