import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { LanguageBadges, LANG_ORDER, formatLanguageList, formatShare, languageLabel } from '../languages.jsx'

const METHOD_LABELS = {
  short_words: 'Коротких слов',
  frequent_words: 'Частотных слов',
  neural_network: 'Нейросетевой',
}

export default function RecognitionPage() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const run = async (event) => {
    event?.preventDefault()
    if (!file) {
      setError('Выберите PDF-файл')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const data = await api.recognize(formData)
      setResult(data)
      setMessage(`Обнаруженные языки: ${formatLanguageList(data.detected_languages, data.shares)}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const methods = Object.entries(result?.results || {}).filter(([, data]) => data && data.method)

  return (
    <>
      <div className="card">
        <h2>Распознавание языка PDF-документа</h2>
        <p className="muted">
          Загрузите документ формата PDF. Если в тексте есть и русский, и немецкий, система покажет
          оба языка и долю каждого. Язык считается найденным при доле не меньше 15%.
        </p>
        <form className="search-bar" onSubmit={run}>
          <input type="file" accept=".pdf,application/pdf" onChange={(event) => setFile(event.target.files[0])} />
          <button type="submit" disabled={loading}>
            {loading ? 'Распознавание...' : 'Распознать'}
          </button>
        </form>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {result && (
        <>
          <div className="card">
            <h2>Результат</h2>
            <p>Обнаруженные языки: {formatLanguageList(result.detected_languages, result.shares)}</p>
            <p>
              <LanguageBadges languages={result.detected_languages} shares={result.shares} />
            </p>
            <p>Длина текста: {result.text_length} символов</p>
            <p>
              Документ сохранён:{' '}
              <Link to={`/documents/${result.document_id}`}>{result.title}</Link>
            </p>
          </div>

          <div className="card">
            <h2>Сравнение методов</h2>
            <table>
              <thead>
                <tr>
                  <th>Метод</th>
                  {LANG_ORDER.map((lang) => (
                    <th key={lang} className="num">{languageLabel(lang)}</th>
                  ))}
                  <th className="num">OoP</th>
                  <th className="num">Время, мс</th>
                </tr>
              </thead>
              <tbody>
                {methods.map(([key, data]) => (
                  <tr key={key}>
                    <td>{METHOD_LABELS[key] || key}</td>
                    {LANG_ORDER.map((lang) => (
                      <td key={lang} className="num">{formatShare(data.shares?.[lang])}</td>
                    ))}
                    <td className="num">{data.oop == null ? '—' : Number(data.oop).toFixed(0)}</td>
                    <td className="num">{data.elapsed_ms ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted">Время метода включает предобработку текста. Кэш лемм сбрасывается перед каждым методом, чтобы сравнение было честным.</p>
          </div>
        </>
      )}
    </>
  )
}
