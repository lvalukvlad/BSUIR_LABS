import { useMemo, useState } from 'react';
import type { DialogSessionInfo } from '../api/client';

type Props = {
  sessions: DialogSessionInfo[];
  currentSessionId: string;
  onSelect: (sessionId: string) => void;
  onCreate: () => Promise<void>;
  onDelete: (sessionId: string) => Promise<void>;
  onRename: (sessionId: string, title: string) => Promise<void>;
};

export default function SessionSidebar({
  sessions,
  currentSessionId,
  onSelect,
  onCreate,
  onDelete,
  onRename,
}: Props) {
  const [search, setSearch] = useState('');
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return sessions;
    return sessions.filter((s) => s.title.toLowerCase().includes(q));
  }, [sessions, search]);

  return (
    <aside className="sessions-sidebar panel">
      <div className="sessions-header">
        <h3>История диалогов</h3>
        <button
          type="button"
          className="btn small"
          onClick={() => void onCreate()}
          title="Создать новую сессию"
        >
          Новый
        </button>
      </div>
      <input
        type="search"
        className="history-search sessions-search"
        placeholder="Поиск по сессиям…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        aria-label="Поиск по сессиям"
      />
      <div className="sessions-list">
        {filtered.length === 0 ? (
          <p className="muted">Сессий пока нет</p>
        ) : (
          filtered.map((s) => (
            <div
              key={s.id}
              className={`session-item ${s.id === currentSessionId ? 'active' : ''}`}
              onClick={() => onSelect(s.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelect(s.id);
              }}
            >
              <div className="session-title">{s.title}</div>
              <div className="session-meta">
                {s.message_count} сообщ.
                  <button
                    type="button"
                    className="btn small ghost"
                    title="Переименовать сессию"
                    onClick={(e) => {
                      e.stopPropagation();
                      const next = window.prompt('Новое название сессии', s.title);
                      if (next && next.trim()) {
                        void onRename(s.id, next.trim());
                      }
                    }}
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    className="btn small danger ghost"
                    title="Удалить сессию"
                    onClick={(e) => {
                      e.stopPropagation();
                      void onDelete(s.id);
                    }}
                  >
                    Удалить
                  </button>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
