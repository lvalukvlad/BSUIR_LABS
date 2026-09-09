import { useState } from 'react';
import DictionaryPanel from './components/DictionaryPanel';
import AnalysisPanel from './components/AnalysisPanel';
import GeneratorPanel from './components/GeneratorPanel';
import HelpPanel from './components/HelpPanel';

type Tab = 'dictionary' | 'analysis' | 'generator' | 'help';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dictionary');

  return (
    <div className="app">
      <header className="header">
        <h1>NLP Словарь</h1>
        <p>Автоматизированная система формирования словаря естественного языка</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'dictionary' ? 'active' : ''}`}
          onClick={() => setActiveTab('dictionary')}
        >
          Словарь
        </button>
        <button
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Анализ текста
        </button>
        <button
          className={`tab ${activeTab === 'generator' ? 'active' : ''}`}
          onClick={() => setActiveTab('generator')}
        >
          Генерация словоформ
        </button>
        <button
          className={`tab ${activeTab === 'help' ? 'active' : ''}`}
          onClick={() => setActiveTab('help')}
        >
          Справка
        </button>
      </nav>

      <main>
        {activeTab === 'dictionary' && <DictionaryPanel />}
        {activeTab === 'analysis' && <AnalysisPanel />}
        {activeTab === 'generator' && <GeneratorPanel />}
        {activeTab === 'help' && <HelpPanel />}
      </main>
    </div>
  );
}

export default App;
