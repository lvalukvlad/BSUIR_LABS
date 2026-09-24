import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [domain, setDomain] = useState('медицина')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Нужен txt или pdf')
      return
    }
    setBusy(true)
    setError('')
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('domain', domain)
      const res = await api.upload(form)
      nav(`/documents/${res.document_id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <div className="card">
        <h2>Построить реферат</h2>
        <p className="muted">
          Кидаешь файл, выбираешь область. Язык смотрится по алфавиту.
        </p>
        <form onSubmit={submit} className="form">
          <label>
            Область
            <select value={domain} onChange={(e) => setDomain(e.target.value)}>
              <option>медицина</option>
              <option>критика изобразительного искусства</option>
            </select>
          </label>
          <label>
            Файл
            <input type="file" accept=".txt,.md,.pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <button type="submit" disabled={busy}>{busy ? 'считаю...' : 'Посчитать'}</button>
        </form>
        {error && <div className="notice error">{error}</div>}
      </div>
      <div className="card">
        <h2>Что уже есть</h2>
        <p className="muted">
          Четыре эталона лежат в коллекции. Открыть можно в <Link to="/documents">документах</Link>.
        </p>
      </div>
    </>
  )
}
