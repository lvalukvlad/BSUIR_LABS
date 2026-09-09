import { useState } from 'react';
import SyntaxPanel from './components/SyntaxPanel';
import HelpPanel from './components/HelpPanel';

type Tab = 'syntax' | 'help';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('syntax');

  return (
    <div className="app">
      <header className="header">
        <h1>Синтаксический анализатор</h1>
        <p>Анализ текста на русском языке</p>
      </header>

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'syntax' ? 'active' : ''}`}
          onClick={() => setActiveTab('syntax')}
        >
          Анализ
        </button>
        <button
          className={`tab ${activeTab === 'help' ? 'active' : ''}`}
          onClick={() => setActiveTab('help')}
        >
          Справка
        </button>
      </nav>

      <main>
        {activeTab === 'syntax' && <SyntaxPanel />}
        {activeTab === 'help' && <HelpPanel />}
      </main>
    </div>
  );
}

export default App;
