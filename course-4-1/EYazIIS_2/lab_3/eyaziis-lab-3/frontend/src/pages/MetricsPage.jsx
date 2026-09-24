import { useState } from 'react'
import { api } from '../api.js'

const fmt = (v) => Number(v).toFixed(3).replace('.', ',')

export default function MetricsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    setBusy(true)
    setError('')
    try {
      setData(await api.metrics())
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const saveCharts = async () => {
    setBusy(true)
    try {
      const res = await api.exportMetrics()
      setMsg(res.message)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <div className="card">
        <h2>Оценка</h2>
        <p className="muted">
          Для эталонов размечены нужные предложения. Сравниваем с первыми десятью.
        </p>
        <div className="actions">
          <button type="button" onClick={run} disabled={busy}>{busy ? 'считаю...' : 'Посчитать'}</button>
          <button type="button" className="secondary" onClick={saveCharts} disabled={busy}>
            Сохранить графики
          </button>
        </div>
      </div>
      {error && <div className="notice error">{error}</div>}
      {msg && <div className="notice success">{msg}</div>}
      {data && (
        <>
          <div className="stats">
            {(data.comparison || []).map((row) => (
              <div className="stat" key={row.model}>
                <b>{fmt(row.f1)}</b>
                <span>F1 · {row.label}</span>
              </div>
            ))}
          </div>
          <div className="card">
            <h2>По документам</h2>
            <table>
              <thead>
                <tr>
                  <th>Документ</th>
                  <th>Язык</th>
                  <th>Область</th>
                  <th className="num">P</th>
                  <th className="num">R</th>
                  <th className="num">F1</th>
                  <th className="num">F1 базы</th>
                  <th className="num">мс</th>
                </tr>
              </thead>
              <tbody>
                {(data.documents || []).map((row) => (
                  <tr key={row.source_file}>
                    <td>{row.title}</td>
                    <td>{row.language}</td>
                    <td>{row.domain}</td>
                    <td className="num">{fmt(row.weighted.precision)}</td>
                    <td className="num">{fmt(row.weighted.recall)}</td>
                    <td className="num">{fmt(row.weighted.f1)}</td>
                    <td className="num">{fmt(row.baseline.f1)}</td>
                    <td className="num">{row.elapsed_ms}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="card">
            <h2>Методы</h2>
            <table>
              <thead>
                <tr>
                  <th>Метод</th>
                  <th className="num">P</th>
                  <th className="num">R</th>
                  <th className="num">F1</th>
                  <th className="num">мс</th>
                </tr>
              </thead>
              <tbody>
                {(data.comparison || []).map((row) => (
                  <tr key={row.model}>
                    <td>{row.label}</td>
                    <td className="num">{fmt(row.precision)}</td>
                    <td className="num">{fmt(row.recall)}</td>
                    <td className="num">{fmt(row.f1)}</td>
                    <td className="num">{Number(row.avg_elapsed_ms || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.groups && (
            <div className="card">
              <h2>По языкам и областям</h2>
              <table>
                <thead>
                  <tr>
                    <th>Группа</th>
                    <th className="num">P</th>
                    <th className="num">R</th>
                    <th className="num">F1</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.groups.language || {}).map(([name, row]) => (
                    <tr key={`lang-${name}`}>
                      <td>язык: {name}</td>
                      <td className="num">{fmt(row.precision)}</td>
                      <td className="num">{fmt(row.recall)}</td>
                      <td className="num">{fmt(row.f1)}</td>
                    </tr>
                  ))}
                  {Object.entries(data.groups.domain || {}).map(([name, row]) => (
                    <tr key={`dom-${name}`}>
                      <td>область: {name}</td>
                      <td className="num">{fmt(row.precision)}</td>
                      <td className="num">{fmt(row.recall)}</td>
                      <td className="num">{fmt(row.f1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {data.charts && (
            <div className="card">
              <h2>Графики</h2>
              {data.charts.method_comparison && (
                <img className="chart" alt="методы" src={`data:image/png;base64,${data.charts.method_comparison}`} />
              )}
              {data.charts.metrics_by_doc && (
                <img className="chart" alt="f1" src={`data:image/png;base64,${data.charts.metrics_by_doc}`} />
              )}
              {data.charts.time_comparison && (
                <img className="chart" alt="время" src={`data:image/png;base64,${data.charts.time_comparison}`} />
              )}
            </div>
          )}
        </>
      )}
    </>
  )
}
