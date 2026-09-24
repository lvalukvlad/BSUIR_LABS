import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function DocumentsPage() {
  const [docs, setDocs] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const reload = () => {
    api.documents().then((data) => setDocs(data.documents)).catch((err) => setError(err.message))
  }

  useEffect(reload, [])

  const remove = async (id) => {
    if (!confirm(`Удалить №${id}?`)) return
    await api.remove(id)
    setMsg('Удалил, веса пересчитал.')
    reload()
  }

  const ru = docs.filter((d) => d.language === 'русский').length
  const de = docs.filter((d) => d.language === 'немецкий').length
  const avgLen = docs.length
    ? Math.round(docs.reduce((s, d) => s + (d.char_len || 0), 0) / docs.length)
    : 0

  return (
    <>
      <div className="stats">
        <div className="stat"><b>{docs.length}</b><span>документов</span></div>
        <div className="stat"><b>{ru}</b><span>русских</span></div>
        <div className="stat"><b>{de}</b><span>немецких</span></div>
        <div className="stat"><b>{avgLen}</b><span>средняя длина</span></div>
      </div>
      {error && <div className="notice error">{error}</div>}
      {msg && <div className="notice success">{msg}</div>}
      <div className="card">
        <h2>Коллекция</h2>
        <p className="muted">Эталоны уже загружены. Свои файлы — с главной.</p>
        <div className="actions no-print">
          <button type="button" className="secondary" onClick={() => window.print()}>Печать</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>Заголовок</th>
              <th>Язык</th>
              <th>Область</th>
              <th>Откуда</th>
              <th className="num">Символы</th>
              <th className="num">мс</th>
              <th className="no-print"></th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id}>
                <td><Link to={`/documents/${d.id}`}>{d.title}</Link></td>
                <td>
                  <span className={`language-badge ${d.language === 'немецкий' ? 'lang-german' : 'lang-russian'}`}>
                    {d.language}
                  </span>
                </td>
                <td>{d.domain}</td>
                <td>
                  <span className={`source-badge ${d.source_kind === 'etalon' ? 'source-etalon' : 'source-upload'}`}>
                    {d.source_kind === 'etalon' ? 'эталон' : 'загрузка'}
                  </span>
                </td>
                <td className="num">{d.char_len}</td>
                <td className="num">{d.elapsed_ms}</td>
                <td className="no-print">
                  <button className="danger" onClick={() => remove(d.id)}>Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
