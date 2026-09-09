import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function HelpPage() {
  const [sections, setSections] = useState([])

  useEffect(() => {
    api
      .help()
      .then((data) => setSections(data.sections))
      .catch(() => setSections([]))
  }, [])

  return (
    <>
      <div className="card">
        <h2>Справка по работе с системой</h2>
        <p className="muted">
          Система выполняет поиск по коллекции русскоязычных документов, используя вероятностную
          модель ранжирования. Ниже описаны основные возможности интерфейса.
        </p>
      </div>

      {sections.map((section) => (
        <div className="card" key={section.title}>
          <h2>{section.title}</h2>
          <ul className="plain">
            {section.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ))}

      <div className="card">
        <h2>Примеры запросов</h2>
        <ul className="plain">
          <li>локальная вычислительная сеть — документ о построении ЛВС;</li>
          <li>нейронные сети и машинное обучение — два тематически связанных документа;</li>
          <li>чёрные дыры и гравитационные волны — запрос с редкими терминами;</li>
          <li>нейроные сети — пример запроса с опечаткой, исправляется автоматически;</li>
          <li>ИИ — аббревиатура, расширяется синонимами из тезауруса.</li>
        </ul>
      </div>
    </>
  )
}
