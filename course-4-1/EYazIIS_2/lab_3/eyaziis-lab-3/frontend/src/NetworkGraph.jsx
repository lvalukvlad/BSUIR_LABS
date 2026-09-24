const COL = {
  ключевое_понятие: '#2f6fed',
  включает: '#2e7d32',
  совстречается_с: '#e65100',
  относится_к: '#6b7684',
  принадлежит: '#8e24aa',
}

function cut(s, n = 26) {
  if (s.length <= n) return s
  return s.slice(0, n - 1) + '…'
}

export default function NetworkGraph({ arcs }) {
  const edges = arcs || []
  if (!edges.length) return <p className="muted">пусто</p>

  const kids = new Map()
  const hasIn = new Set()
  const names = new Set()
  for (const e of edges) {
    names.add(e.source)
    names.add(e.target)
    hasIn.add(e.target)
    if (!kids.has(e.source)) kids.set(e.source, [])
    if (e.relation !== 'совстречается_с' && e.relation !== 'принадлежит') {
      kids.get(e.source).push(e.target)
    }
  }

  const roots = [...names].filter((x) => !hasIn.has(x))
  const layers = []
  const seen = new Set()
  let cur = roots.length ? roots : [...names].slice(0, 1)
  while (cur.length && layers.length < 5) {
    const uniq = [...new Set(cur)].filter((x) => !seen.has(x))
    if (!uniq.length) break
    layers.push(uniq)
    uniq.forEach((x) => seen.add(x))
    cur = uniq.flatMap((x) => kids.get(x) || [])
  }
  const leftover = [...names].filter((x) => !seen.has(x))
  if (leftover.length) layers.push(leftover)

  const w = 780
  const rowH = 92
  const h = 70 + layers.length * rowH
  const pts = new Map()
  layers.forEach((layer, d) => {
    layer.forEach((name, i) => {
      const x = layer.length === 1 ? w / 2 : 50 + (i * (w - 100)) / (layer.length - 1)
      pts.set(name, { name, x, y: 36 + d * rowH })
    })
  })

  return (
    <div className="network-wrap">
      <svg viewBox={`0 0 ${w} ${h}`} className="network">
        {edges.map((e, i) => {
          const a = pts.get(e.source)
          const b = pts.get(e.target)
          if (!a || !b) return null
          return (
            <line
              key={`${e.source}-${e.relation}-${e.target}-${i}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke={COL[e.relation] || '#9aa5b1'}
              strokeWidth="1.4"
            />
          )
        })}
        {[...pts.values()].map((p) => (
          <g key={p.name}>
            <circle cx={p.x} cy={p.y} r="7" fill="#fff" stroke="#2f6fed" strokeWidth="2" />
            <text x={p.x} y={p.y - 14} textAnchor="middle" fontSize="11" fill="#1f2933">
              {cut(p.name)}
            </text>
          </g>
        ))}
      </svg>
      <ul className="legend">
        <li><span style={{ background: COL.ключевое_понятие }} /> ключевое понятие</li>
        <li><span style={{ background: COL.включает }} /> включает</li>
        <li><span style={{ background: COL.совстречается_с }} /> совстречается</li>
        <li><span style={{ background: COL.относится_к }} /> относится к области</li>
        <li><span style={{ background: COL.принадлежит }} /> принадлежит</li>
      </ul>
    </div>
  )
}
