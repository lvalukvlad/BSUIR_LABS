import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function HelpPage() {
  const [sections, setSections] = useState([])

  useEffect(() => {
    api.help().then((data) => setSections(data.sections || [])).catch(() => setSections([]))
  }, [])

  return (
    <>
      <div className="card">
        <h2>Справка по работе с системой</h2>
        <p className="muted">
          Система распознаёт языки PDF-документа. Если в тексте есть и русский, и немецкий,
          на экране видны оба. Используются три метода: коротких слов, частотных слов и нейросетевой.
        </p>
      </div>

      {sections.map((section, i) => (
        <div className="card" key={i}>
          <h2>{section.title}</h2>
          <ul className="plain">
            {section.items.map((item, j) => <li key={j}>{item}</li>)}
          </ul>
        </div>
      ))}

      <div className="card">
        <h2>Описание методов</h2>
        <ul className="plain">
          <li><strong>Коротких слов:</strong> анализирует лексемы длиной до 5 символов, сравнивает частотный профиль.</li>
          <li><strong>Частотных слов:</strong> строит ПОЯ из 50 самых частотных слов, сравнивает вероятности.</li>
          <li><strong>Нейросетевой:</strong> MLP-нейросеть на sklearn, использует бинарные N-граммы (N=1..5) как признаки.</li>
        </ul>
      </div>
    </>
  )
}