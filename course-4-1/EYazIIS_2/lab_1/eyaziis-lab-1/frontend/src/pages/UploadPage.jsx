import { useState } from 'react'
import { api } from '../api.js'

export default function UploadPage() {
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const reset = () => {
    setMessage('')
    setError('')
  }

  const submitText = async (event) => {
    event.preventDefault()
    reset()
    setBusy(true)
    try {
      const result = await api.addDocument({ title, text })
      setMessage(`${result.message} (идентификатор ${result.document_id})`)
      setTitle('')
      setText('')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const submitFile = async (event) => {
    event.preventDefault()
    reset()
    if (!file) {
      setError('Выберите файл для загрузки')
      return
    }
    setBusy(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const result = await api.uploadDocument(formData)
      setMessage(`${result.message}: «${result.title}», извлечено ${result.characters} символов`)
      setFile(null)
      event.target.reset()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      {message && <div className="notice success">{message}</div>}
      {error && <div className="notice error">{error}</div>}

      <div className="card">
        <h2>Добавить документ вводом текста</h2>
        <form onSubmit={submitText}>
          <label>Заголовок</label>
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />
          <label style={{ marginTop: 10, display: 'block' }}>Текст документа</label>
          <textarea
            rows="10"
            value={text}
            onChange={(event) => setText(event.target.value)}
            required
          />
          <button type="submit" style={{ marginTop: 12 }} disabled={busy}>
            Проиндексировать
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Загрузить документ из файла</h2>
        <p className="muted">
          Поддерживаемые форматы: .txt, .md, .csv, .log, .html, .rtf, .pdf, .docx
        </p>
        <form onSubmit={submitFile}>
          <input type="file" onChange={(event) => setFile(event.target.files[0])} />
          <button type="submit" style={{ marginTop: 12 }} disabled={busy}>
            Загрузить и проиндексировать
          </button>
        </form>
      </div>
    </>
  )
}
