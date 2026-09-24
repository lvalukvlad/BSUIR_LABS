import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function HelpPage() {
  const [blocks, setBlocks] = useState([])

  useEffect(() => {
    api.help().then((data) => setBlocks(data.sections || [])).catch(() => setBlocks([]))
  }, [])

  return (
    <>
      <div className="card">
        <h2>Справка</h2>
        <p className="muted">Коротко про вес предложений и про сеть понятий.</p>
      </div>
      {blocks.map((block) => (
        <div className="card" key={block.title}>
          <h2>{block.title}</h2>
          <ul className="plain">
            {block.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </>
  )
}
