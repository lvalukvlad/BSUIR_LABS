import { useState } from 'react';
import CorpusPanel from './components/CorpusPanel';
import StatisticsPanel from './components/StatisticsPanel';
import SearchPanel from './components/SearchPanel';
import HelpPanel from './components/HelpPanel';

type Tab = 'corpus' | 'statistics' | 'search' | 'help';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('corpus');

  return (
    <div className="app">
      <header className="header">
        <h1>Корпусный менеджер</h1>
        <p>Управление кулинарным корпусом текстов</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'corpus' ? 'active' : ''}`}
          onClick={() => setActiveTab('corpus')}
        >
          Корпус
        </button>
        <button
          className={`tab ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          Статистика
        </button>
        <button
          className={`tab ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          Поиск
        </button>
        <button
          className={`tab ${activeTab === 'help' ? 'active' : ''}`}
          onClick={() => setActiveTab('help')}
        >
          Справка
        </button>
      </nav>

      <main>
        {activeTab === 'corpus' && <CorpusPanel />}
        {activeTab === 'statistics' && <StatisticsPanel />}
        {activeTab === 'search' && <SearchPanel />}
        {activeTab === 'help' && <HelpPanel />}
      </main>
    </div>
  );
}

export default App;
