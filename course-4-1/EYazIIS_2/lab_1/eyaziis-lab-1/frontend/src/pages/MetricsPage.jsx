import { useState } from 'react'
import { api } from '../api.js'

const format = (value) => Number(value).toFixed(3).replace('.', ',')

export default function MetricsPage() {
  const [topK, setTopK] = useState(10)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      setData(await api.metrics(Number(topK)))
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
      const result = await api.exportMetrics(Number(topK))
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
        <h2>Оценка качества работы системы</h2>
        <p className="muted">
          Оценка выполняется на эталонных запросах с заранее размеченными релевантными
          документами. Для каждого запроса система выполняет реальный поиск, после чего
          вычисляются метрики полноты, точности и ранговые метрики качества.
        </p>
        <div className="options">
          <div>
            <label>Глубина выдачи (k)</label>
            <input
              type="number"
              min="1"
              max="30"
              value={topK}
              onChange={(event) => setTopK(event.target.value)}
            />
          </div>
          <div className="checkbox">
            <button onClick={run} disabled={busy}>
              {busy ? 'Расчёт...' : 'Рассчитать метрики'}
            </button>
          </div>
          <div className="checkbox">
            <button className="secondary" onClick={exportCharts} disabled={busy}>
              Выгрузить графики в отчёт
            </button>
          </div>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {main && (
        <>
          <div className="card">
            <h2>Метрики по эталонным запросам ({main.summary.label})</h2>
            <table>
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Запрос</th>
                  <th className="num">Rel</th>
                  <th className="num">P</th>
                  <th className="num">R</th>
                  <th className="num">F1</th>
                  <th className="num">P@5</th>
                  <th className="num">R-Prec</th>
                  <th className="num">AP</th>
                  <th className="num">nDCG</th>
                </tr>
              </thead>
              <tbody>
                {main.per_query.map((row) => (
                  <tr key={row.code}>
                    <td>{row.code}</td>
                    <td>{row.query}</td>
                    <td className="num">{row.relevant_count}</td>
                    <td className="num">{format(row.precision)}</td>
                    <td className="num">{format(row.recall)}</td>
                    <td className="num">{format(row.f1)}</td>
                    <td className="num">{format(row.p5)}</td>
                    <td className="num">{format(row.r_precision)}</td>
                    <td className="num">{format(row.average_precision)}</td>
                    <td className="num">{format(row.ndcg10)}</td>
                  </tr>
                ))}
                <tr className="total">
                  <td colSpan="3">Среднее по коллекции</td>
                  <td className="num">{format(main.summary.precision)}</td>
                  <td className="num">{format(main.summary.recall)}</td>
                  <td className="num">{format(main.summary.f1)}</td>
                  <td className="num">{format(main.summary.p5)}</td>
                  <td className="num">{format(main.summary.r_precision)}</td>
                  <td className="num">{format(main.summary.map)}</td>
                  <td className="num">{format(main.summary.ndcg10)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <h2>Сравнение моделей ранжирования</h2>
            <table>
              <thead>
                <tr>
                  <th>Модель</th>
                  <th className="num">P</th>
                  <th className="num">R</th>
                  <th className="num">F1</th>
                  <th className="num">F0.5</th>
                  <th className="num">F2</th>
                  <th className="num">P@5</th>
                  <th className="num">P@10</th>
                  <th className="num">MAP</th>
                  <th className="num">nDCG@10</th>
                </tr>
              </thead>
              <tbody>
                {data.comparison.map((row) => (
                  <tr key={row.model}>
                    <td>{row.label}</td>
                    <td className="num">{format(row.precision)}</td>
                    <td className="num">{format(row.recall)}</td>
                    <td className="num">{format(row.f1)}</td>
                    <td className="num">{format(row.f05)}</td>
                    <td className="num">{format(row.f2)}</td>
                    <td className="num">{format(row.p5)}</td>
                    <td className="num">{format(row.p10)}</td>
                    <td className="num">{format(row.map)}</td>
                    <td className="num">{format(row.ndcg10)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.charts && (
            <div className="card">
              <h2>Графическое представление результатов</h2>
              <img
                className="chart"
                alt="Метрики по запросам"
                src={`data:image/png;base64,${data.charts.metrics_by_query}`}
              />
              <img
                className="chart"
                alt="Кривая полноты-точности"
                src={`data:image/png;base64,${data.charts.pr_curve}`}
              />
              <img
                className="chart"
                alt="Сравнение моделей"
                src={`data:image/png;base64,${data.charts.model_comparison}`}
              />
            </div>
          )}
        </>
      )}
    </>
  )
}
