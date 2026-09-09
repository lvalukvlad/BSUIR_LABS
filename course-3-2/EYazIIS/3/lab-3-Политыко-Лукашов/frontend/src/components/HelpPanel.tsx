import { useState, useEffect } from 'react';

interface HelpData {
  title: string;
  description: string;
  features: string[];
  endpoints: Record<string, string>;
  syntax_roles: Record<string, string>;
}

function HelpPanel() {
  const [help, setHelp] = useState<HelpData | null>(null);

  useEffect(() => {
    fetch('/api/help')
      .then(res => res.json())
      .then(data => setHelp(data))
      .catch(err => console.error('Failed to load help:', err));
  }, []);

  if (!help) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="panel">
      <h2>{help.title}</h2>
      <p style={{ marginBottom: '1.5rem' }}>{help.description}</p>

      <div className="help-content">
        <h3>Возможности</h3>
        <ul>
          {help.features.map((feature, idx) => (
            <li key={idx}>{feature}</li>
          ))}
        </ul>

        <h3>API Endpoints</h3>
        <ul>
          {Object.entries(help.endpoints).map(([endpoint, description]) => (
            <li key={endpoint}>
              <code>{endpoint}</code> — {description}
            </li>
          ))}
        </ul>

        <h3>Члены предложения</h3>
        <ul>
          {Object.entries(help.syntax_roles).map(([role, description]) => (
            <li key={role}>
              <strong>{role}</strong>: {description}
            </li>
          ))}
        </ul>

        <h3>Инструкция</h3>
        <ol>
          <li>Введите текст в поле "Анализ текста" или загрузите файл (TXT, RTF)</li>
          <li>Нажмите "Анализировать текст" или кнопку "Анализ" рядом с документом</li>
          <li>Просмотрите результаты в таблице: слово, часть речи, лемма, грамматические признаки, член предложения</li>
          <li>Вы можете редактировать члены предложения в выпадающем списке</li>
          <li>Статистика показывает распределение частей речи и членов предложения</li>
        </ol>
      </div>
    </div>
  );
}

export default HelpPanel;
