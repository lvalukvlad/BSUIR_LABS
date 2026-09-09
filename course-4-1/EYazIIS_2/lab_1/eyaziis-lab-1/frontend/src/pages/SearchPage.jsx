import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [model, setModel] = useState('bm25')
  const [usePrf, setUsePrf] = useState(false)
  const [topK, setTopK] = useState(10)
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const skipSuggest = useRef(false)

  useEffect(() => {
    if (skipSuggest.current) {
      skipSuggest.current = false
      return
    }
    const lastWord = query.split(/\s+/).pop() || ''
    if (lastWord.length < 2) {
      setSuggestions([])
      return
    }
    const timer = setTimeout(() => {
      api
        .suggest(lastWord)
        .then((data) => {
          setSuggestions(data.suggestions)
          setShowSuggestions(true)
        })
        .catch(() => setSuggestions([]))
    }, 220)
    return () => clearTimeout(timer)
  }, [query])

  const applySuggestion = (term) => {
    const words = query.split(/\s+/)
    words[words.length - 1] = term
    skipSuggest.current = true
    setQuery(words.join(' ') + ' ')
    setShowSuggestions(false)
  }

  const runSearch = async (event) => {
    event?.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setShowSuggestions(false)
    try {
      const data = await api.search({
        query,
        top_k: Number(topK),
        model,
        use_prf: usePrf,
        date_from: dateFrom || null,
        date_to: dateTo || null,
      })
      setResponse(data)
    } catch (err) {
      setError(err.message)
      setResponse(null)
    } finally {
      setLoading(false)
    }
  }

  const analysis = response?.analysis

  return (
    <>
      <div className="card">
        <form className="search-bar" onSubmit={runSearch}>
          <input
            type="text"
            value={query}
            placeholder="Введите запрос на естественном языке, например: нейронные сети и обучение"
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => suggestions.length && setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Поиск...' : 'Найти'}
          </button>
          {showSuggestions && suggestions.length > 0 && (
            <div className="suggestions">
              {suggestions.map((term) => (
                <div key={term} onMouseDown={() => applySuggestion(term)}>
                  {term}
                </div>
              ))}
            </div>
          )}
        </form>

        <div className="options">
          <div>
            <label>Модель ранжирования</label>
            <select value={model} onChange={(event) => setModel(event.target.value)}>
              <option value="bm25">Вероятностная (BM25)</option>
              <option value="tfidf">Векторная (TF-IDF)</option>
            </select>
          </div>
          <div>
            <label>Размер выдачи</label>
            <input
              type="number"
              min="1"
              max="50"
              value={topK}
              onChange={(event) => setTopK(event.target.value)}
            />
          </div>
          <div>
            <label>Дата с</label>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          </div>
          <div>
            <label>Дата по</label>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          </div>
          <div className="checkbox">
            <input
              id="prf"
              type="checkbox"
              checked={usePrf}
              disabled={model !== 'bm25'}
              onChange={(event) => setUsePrf(event.target.checked)}
            />
            <label htmlFor="prf" style={{ margin: 0 }}>
              Обратная связь
            </label>
          </div>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}

      {analysis?.corrections?.length > 0 && (
        <div className="notice">
          Возможно, вы имели в виду: <b>{analysis.corrected}</b> (исправлено:{' '}
          {analysis.corrections.map((c) => `${c.from} → ${c.to}`).join(', ')})
        </div>
      )}

      {response && (
        <div className="card">
          <h2>
            Найдено документов: {response.total}{' '}
            <span className="muted" style={{ fontWeight: 400, fontSize: 13 }}>
              за {response.elapsed_ms} мс, модель {response.model.toUpperCase()}
              {response.prf_enabled ? ' с обратной связью' : ''}
            </span>
          </h2>

          {analysis && (
            <div className="meta" style={{ marginBottom: 10 }}>
              <span>Поисковый образ запроса: {analysis.lemmas.join(', ') || '—'}</span>
              {analysis.added_synonyms.length > 0 && (
                <span>Добавлено синонимов: {analysis.added_synonyms.join(', ')}</span>
              )}
            </div>
          )}

          {response.results.length === 0 && (
            <p className="muted">
              По запросу ничего не найдено. Попробуйте изменить формулировку или проверьте
              подсказки при вводе.
            </p>
          )}

          {response.results.map((item) => (
            <div className="result" key={item.document_id}>
              <div className="result-head">
                <Link to={`/documents/${item.document_id}?q=${encodeURIComponent(query)}`}>
                  {item.title}
                </Link>
                <span className="rank">RSV = {item.rank}</span>
              </div>
              <p className="snippet" dangerouslySetInnerHTML={{ __html: item.snippet }} />
              <div className="meta">
                <span>Позиция: {item.position}</span>
                <span>Дата: {item.date}</span>
                <span>Длина: {item.doc_len} терминов</span>
                {item.source_file && <span>Файл: {item.source_file}</span>}
              </div>
              {item.matched_words.length > 0 && (
                <div className="chips">
                  <span className="muted" style={{ fontSize: 13 }}>
                    Слова запроса в документе:
                  </span>
                  {item.matched_words.slice(0, 12).map((word, index) => (
                    <span className="chip" key={`${word}-${index}`}>
                      {word}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {response?.term_weights?.length > 0 && (
        <div className="card">
          <h2>Веса терминов запроса</h2>
          <table>
            <thead>
              <tr>
                <th>Термин</th>
                <th className="num">Документная частота</th>
                <th className="num">Вес Робертсона — Спарк Джонс</th>
              </tr>
            </thead>
            <tbody>
              {response.term_weights.map((term) => (
                <tr key={term.term}>
                  <td>{term.term}</td>
                  <td className="num">{term.df}</td>
                  <td className="num">{term.weight.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
