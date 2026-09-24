import { useState } from 'react'
import { api } from '../api.js'

const format = (value) => Number(value).toFixed(3).replace('.', ',')

export default function MetricsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      setData(await api.metrics())
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const exportCharts = async () => {
    setBusy(true)
    setError('')
    try {
      const result = await api.exportMetrics()
      setMessage(result.message)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const main = data?.main

  return (
    <>
      <div className="card">
        <h2>Оценка качества распознавания</h2>
        <p className="muted">
          Оценка выполняется на эталонных текстах с заранее известным набором языков. Для каждого
          текста система запускает три метода и сравнивает найденные языки с эталоном.
        </p>
        <div className="options">
          <button onClick={run} disabled={busy}>
            {busy ? 'Расчёт...' : 'Рассчитать метрики'}
          </button>
          <button className="secondary" onClick={exportCharts} disabled={busy}>
            Выгрузить графики в отчёт
          </button>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {main && (
        <>
          <div className="card">
            <h2>Результаты по эталонным текстам ({main.summary.label})</h2>
            <table>
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Текст</th>
                  <th>Эталон</th>
                  <th>Предсказано</th>
                  <th>Верно</th>
                  <th className="num">мс</th>
                </tr>
              </thead>
              <tbody>
                {main.per_query.map((row) => (
                  <tr key={row.code}>
                    <td>{row.code}</td>
                    <td>{row.query}</td>
                    <td>{(row.relevant || []).join(', ')}</td>
                    <td>{Array.isArray(row.predicted) ? row.predicted.join(', ') : row.predicted}</td>
                    <td>{row.correct ? 'да' : 'нет'}</td>
                    <td className="num">{Number(row.elapsed_ms || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h2>Сравнение методов</h2>
            <table>
              <thead>
                <tr>
                  <th>Метод</th>
                  <th className="num">Accuracy</th>
                  <th className="num">P</th>
                  <th className="num">R</th>
                  <th className="num">F1</th>
                  <th className="num">F0.5</th>
                  <th className="num">F2</th>
                  <th className="num">мс</th>
                </tr>
              </thead>
              <tbody>
                {(data.comparison || []).map((row) => (
                  <tr key={row.model}>
                    <td>{row.label}</td>
                    <td className="num">{format(row.accuracy)}</td>
                    <td className="num">{format(row.precision)}</td>
                    <td className="num">{format(row.recall)}</td>
                    <td className="num">{format(row.f1)}</td>
                    <td className="num">{format(row.f05)}</td>
                    <td className="num">{format(row.f2)}</td>
                    <td className="num">{Number(row.avg_elapsed_ms || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.charts && (
            <div className="card">
              <h2>Графическое представление результатов</h2>
              {data.charts.method_comparison && (
                <img className="chart" alt="Сравнение методов" src={`data:image/png;base64,${data.charts.method_comparison}`} />
              )}
              {data.charts.time_comparison && (
                <img className="chart" alt="Быстродействие" src={`data:image/png;base64,${data.charts.time_comparison}`} />
              )}
              {data.charts.metrics_by_query && (
                <img className="chart" alt="Эталонные тексты" src={`data:image/png;base64,${data.charts.metrics_by_query}`} />
              )}
            </div>
          )}
        </>
      )}
    </>
  )
}
