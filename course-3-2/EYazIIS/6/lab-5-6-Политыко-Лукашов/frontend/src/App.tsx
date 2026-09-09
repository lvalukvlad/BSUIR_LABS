import { useState } from 'react';
import ChatPanel from './components/ChatPanel';
import HelpPanel from './components/HelpPanel';

type Tab = 'dialog' | 'help';

export default function App() {
  const [tab, setTab] = useState<Tab>('dialog');

  return (
    <div className="app">
      <header className="header">
        <h1>Диалоговая система</h1>
        <p>Русский язык · Медицина</p>
      </header>

      <nav className="tabs" aria-label="Разделы">
        <button
          type="button"
          className={`tab ${tab === 'dialog' ? 'active' : ''}`}
          onClick={() => setTab('dialog')}
        >
          Диалог
        </button>
        <button
          type="button"
          className={`tab ${tab === 'help' ? 'active' : ''}`}
          onClick={() => setTab('help')}
        >
          Справка
        </button>
      </nav>

      <main className="main-wide">{tab === 'dialog' ? <ChatPanel /> : <HelpPanel />}</main>
    </div>
  );
}
