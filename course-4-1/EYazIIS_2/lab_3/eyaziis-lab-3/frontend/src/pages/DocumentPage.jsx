import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api.js'
import NetworkGraph from '../NetworkGraph.jsx'

function KeywordTree({ nodes }) {
  if (!nodes?.length) return null
  return (
    <ul className="tree">
      {nodes.map((n) => (
        <li key={n.term}>
          <strong>{n.term}</strong>
          <span className="muted"> {Number(n.weight).toFixed(2)}</span>
          <KeywordTree nodes={n.children} />
        </li>
      ))}
    </ul>
  )
}

function SourceText({ sents }) {
  if (!sents?.length) return null
  return (
    <div className="doc-text">
      {sents.map((s) => (
        <span key={s.index} className={s.selected ? 'picked' : undefined}>
          {s.selected ? <mark>{s.text}</mark> : s.text}
          {' '}
        </span>
      ))}
    </div>
  )
}

export default function DocumentPage() {
  const { id } = useParams()
  const [doc, setDoc] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.document(id).then(setDoc).catch((err) => setError(err.message))
  }, [id])

  if (error) return <div className="notice error">{error}</div>
  if (!doc) return <div className="card">загрузка...</div>

  const sents = doc.sentences_json || []

  return (
    <>
      <div className="card">
        <h2>{doc.title}</h2>
        <div className="meta">
          <span className={`language-badge ${doc.language === 'немецкий' ? 'lang-german' : 'lang-russian'}`}>
            {doc.language}
          </span>
          <span className="source-badge source-etalon">{doc.domain}</span>
          <span>{doc.char_len} симв.</span>
          <span>{sents.length} предл.</span>
          <span>{doc.elapsed_ms} мс</span>
        </div>
        <div className="actions no-print">
          <a className="button" href={api.exportUrl(id)}>Скачать txt</a>
          <button type="button" className="secondary" onClick={() => window.print()}>Печать</button>
          <a href="#source">К тексту</a>
          <Link to="/documents">Назад</Link>
        </div>
      </div>

      <div className="card">
        <h2>Классический реферат</h2>
        <p className="muted">10 предложений с наибольшим весом, в порядке текста.</p>
        <p className="doc-text">{doc.summary_classic}</p>
      </div>

      <div className="card">
        <h2>Базовый</h2>
        <p className="muted">Просто первые 10, без весов.</p>
        <p className="doc-text">{doc.baseline_classic}</p>
      </div>

      <div className="card">
        <h2>Ключевые слова</h2>
        <KeywordTree nodes={doc.keywords_json} />
      </div>

      <div className="card">
        <h2>Сеть</h2>
        <NetworkGraph arcs={doc.network_json} />
        <ul className="plain">
          {(doc.network_json || []).map((arc, i) => (
            <li key={`${arc.source}-${arc.target}-${i}`}>
              {arc.source} — {arc.relation} — {arc.target}
            </li>
          ))}
        </ul>
      </div>

      <div className="card no-print">
        <h2>Веса</h2>
        <table>
          <thead>
            <tr>
              <th className="num">№</th>
              <th>Предложение</th>
              <th className="num">Posd</th>
              <th className="num">Posp</th>
              <th className="num">Score</th>
              <th className="num">Вес</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {sents.map((s) => (
              <tr key={s.index} className={s.selected ? 'picked-row' : undefined}>
                <td className="num">{s.index}</td>
                <td>{s.text}</td>
                <td className="num">{Number(s.posd).toFixed(3)}</td>
                <td className="num">{Number(s.posp).toFixed(3)}</td>
                <td className="num">{Number(s.score).toFixed(2)}</td>
                <td className="num">{Number(s.weight).toFixed(2)}</td>
                <td>{s.selected ? 'да' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card" id="source">
        <h2>Исходный текст</h2>
        <p className="muted no-print">Жёлтым — то, что попало в реферат.</p>
        <SourceText sents={sents} />
      </div>
    </>
  )
}
