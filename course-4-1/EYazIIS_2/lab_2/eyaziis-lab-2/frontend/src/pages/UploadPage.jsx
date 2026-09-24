import { useState } from 'react'
import { api } from '../api.js'
import { formatLanguageList } from '../languages.jsx'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submitFile = async (event) => {
    event.preventDefault()
    reset()
    if (!file) {
      setError('Выберите PDF-файл')
      return
    }
    setBusy(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const result = await api.recognize(formData)
      setMessage(`Документ распознан: ${formatLanguageList(result.detected_languages, result.shares)}`)
      setFile(null)
      event.target.reset()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const reset = () => { setMessage(''); setError('') }

  return (
    <>
      {message && <div className="notice success">{message}</div>}
      {error && <div className="notice error">{error}</div>}
      <div className="card">
        <h2>Загрузить PDF-документ</h2>
        <p className="muted">Поддерживаемый формат: PDF. Система показывает все языки, которые есть в тексте.</p>
        <form onSubmit={submitFile}>
          <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
          <button type="submit" style={{ marginTop: 12 }} disabled={busy}>
            {busy ? 'Распознавание...' : 'Загрузить и распознать'}
          </button>
        </form>
      </div>
    </>
  )
}