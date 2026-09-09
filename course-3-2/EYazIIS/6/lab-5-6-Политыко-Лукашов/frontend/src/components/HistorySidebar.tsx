import { useState } from 'react';
import type { DialogMessage } from '../api/client';

type Props = {
  messages: DialogMessage[];
  filter: string;
  onFilterChange: (v: string) => void;
  onRefresh: () => void;
  onPatch: (id: number, content: string) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onClear: () => Promise<void>;
};

export default function HistorySidebar({
  messages,
  filter,
  onFilterChange,
  onRefresh,
  onPatch,
  onDelete,
  onClear,
}: Props) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState(false);

  const startEdit = (m: DialogMessage) => {
    setEditingId(m.id);
    setDraft(m.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setDraft('');
  };

  const saveEdit = async () => {
    if (editingId == null) return;
    setBusy(true);
    try {
      await onPatch(editingId, draft);
      cancelEdit();
      await onRefresh();
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: number) => {
    if (!window.confirm('Удалить это сообщение из истории?')) return;
    setBusy(true);
    try {
      await onDelete(id);
      if (editingId === id) cancelEdit();
      await onRefresh();
    } finally {
      setBusy(false);
    }
  };

  const clearAll = async () => {
    if (!window.confirm('Очистить историю текущей сессии?')) return;
    setBusy(true);
    try {
      await onClear();
      cancelEdit();
      await onRefresh();
    } finally {
      setBusy(false);
    }
  };

  return (
    <aside className="history-sidebar">
      <div className="history-header">
        <h2>История</h2>
        <button type="button" className="btn danger ghost" onClick={clearAll} disabled={busy}>
          Очистить
        </button>
      </div>
      <input
        type="search"
        className="history-search"
        placeholder="Поиск по тексту…"
        value={filter}
        onChange={(e) => onFilterChange(e.target.value)}
        aria-label="Фильтр истории"
      />
      <p className="history-hint">Редактирование и удаление записей текущей сессии.</p>
      <div className="history-list">
        {messages.length === 0 ? (
          <p className="muted">{filter.trim() ? 'Нет совпадений' : 'Пока нет сообщений'}</p>
        ) : (
          messages.map((m) => (
            <div key={m.id} className={`history-item role-${m.role}`}>
              <div className="history-meta">
                <span className="badge">{m.role === 'user' ? 'Вы' : 'Система'}</span>
                {m.role === 'assistant' && m.intent ? (
                  <span className="intent" title="Намерение">
                    {m.intent} · {m.processing_time_ms} мс
                  </span>
                ) : null}
              </div>
              {editingId === m.id ? (
                <div className="edit-block">
                  <textarea
                    className="edit-area"
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    rows={4}
                  />
                  <div className="edit-actions">
                    <button type="button" className="btn" onClick={saveEdit} disabled={busy}>
                      Сохранить
                    </button>
                    <button type="button" className="btn ghost" onClick={cancelEdit} disabled={busy}>
                      Отмена
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <pre className="history-text">{m.content}</pre>
                  <div className="history-actions">
                    <button type="button" className="btn small ghost" onClick={() => startEdit(m)} disabled={busy}>
                      Изменить
                    </button>
                    <button type="button" className="btn small danger ghost" onClick={() => remove(m.id)} disabled={busy}>
                      Удалить
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
