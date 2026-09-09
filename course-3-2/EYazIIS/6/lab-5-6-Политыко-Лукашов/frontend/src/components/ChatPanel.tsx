import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CorpusSource, DialogMessage, DialogSessionInfo } from '../api/client';
import { api } from '../api/client';
import SessionSidebar from './SessionSidebar';

export default function ChatPanel() {
  const [sessions, setSessions] = useState<DialogSessionInfo[]>([]);
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<DialogMessage[]>([]);
  const [sourcesByMsg, setSourcesByMsg] = useState<Record<number, CorpusSource[]>>({});
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [histFilter, setHistFilter] = useState('');
  const [stats, setStats] = useState<{ corpus_chunks: number; messages_total: number } | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState('');
  const [editingBusy, setEditingBusy] = useState(false);
  const [versionView, setVersionView] = useState<Record<number, number>>({});
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const refreshSessions = useCallback(async () => {
    const { sessions: list } = await api.listSessions();
    setSessions(list);
    if (!sessionId && list.length > 0) {
      setSessionId(list[0].id);
    }
    return list;
  }, [sessionId]);

  const load = useCallback(async () => {
    if (!sessionId) {
      setMessages([]);
      setSourcesByMsg({});
      return;
    }
    const { messages: list } = await api.getHistory(sessionId);
    setMessages(list);
    const srcMap: Record<number, CorpusSource[]> = {};
    for (const m of list) {
      if (m.role === 'assistant' && m.sources?.length) {
        srcMap[m.id] = m.sources;
      }
    }
    setSourcesByMsg(srcMap);
    const vv: Record<number, number> = {};
    for (const m of list) {
      if (m.role === 'user' && m.versions) {
        vv[m.id] = m.versions.length;
      }
    }
    setVersionView(vv);
  }, [sessionId]);

  const loadStats = useCallback(async () => {
    try {
      const s = await api.getStats();
      setStats({ corpus_chunks: s.corpus_chunks, messages_total: s.messages_total });
    } catch {
      setStats(null);
    }
  }, []);

  useEffect(() => {
    refreshSessions().catch((e) => setError(String(e)));
    loadStats();
  }, [refreshSessions, loadStats]);

  useEffect(() => {
    setError(null);
    load().catch((e) => setError(String(e)));
  }, [load, sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const send = async () => {
    const text = input.trim();
    if (!text || sending || !sessionId) return;
    setSending(true);
    setError(null);
    try {
      const out = await api.sendMessage(text, sessionId);
      setInput('');
      if (out.sources?.length && out.assistant_message?.id) {
        setSourcesByMsg((prev) => ({
          ...prev,
          [out.assistant_message.id]: out.sources,
        }));
      }
      await load();
      await refreshSessions();
      await loadStats();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSending(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const newSession = async () => {
    const s = await api.createSession(`Диалог ${new Date().toLocaleString('ru-RU')}`);
    await refreshSessions();
    setSessionId(s.id);
  };

  const removeSession = async (id: string) => {
    if (!window.confirm('Удалить эту сессию целиком?')) return;
    await api.deleteSession(id);
    const list = await refreshSessions();
    if (sessionId === id) {
      if (list.length > 0) {
        setSessionId(list[0].id);
      } else {
        const created = await api.createSession('Новый диалог');
        await refreshSessions();
        setSessionId(created.id);
      }
    }
  };

  const renameSession = async (id: string, title: string) => {
    try {
      await api.renameSession(id, title);
      await refreshSessions();
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const exportJson = async () => {
    if (!sessionId) return;
    const data = await api.exportSession(sessionId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `dialog-${sessionId.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const filteredSidebarMessages = useMemo(() => {
    const q = histFilter.trim().toLowerCase();
    if (!q) return messages;
    return messages.filter((m) => m.content.toLowerCase().includes(q));
  }, [messages, histFilter]);

  const prevUserByAssistantId = useMemo(() => {
    const map: Record<number, DialogMessage | undefined> = {};
    let lastUser: DialogMessage | undefined;
    for (const m of messages) {
      if (m.role === 'user') {
        lastUser = m;
      } else if (m.role === 'assistant') {
        map[m.id] = lastUser;
      }
    }
    return map;
  }, [messages]);

  const getUserShownText = (m: DialogMessage): string => {
    if (m.role !== 'user' || !m.versions?.length) return m.content;
    const idx = versionView[m.id] ?? m.versions.length;
    if (idx < m.versions.length) return m.versions[idx].user;
    return m.content;
  };

  const getAssistantShown = (assistant: DialogMessage, prevUser?: DialogMessage) => {
    if (!prevUser || prevUser.role !== 'user' || !prevUser.versions?.length) {
      return {
        content: assistant.content,
        intent: assistant.intent,
        processing_time_ms: assistant.processing_time_ms,
      };
    }
    const idx = versionView[prevUser.id] ?? prevUser.versions.length;
    if (idx < prevUser.versions.length) {
      const v = prevUser.versions[idx];
      return {
        content: v.assistant,
        intent: v.intent || assistant.intent,
        processing_time_ms: v.processing_time_ms ?? assistant.processing_time_ms,
      };
    }
    return {
      content: assistant.content,
      intent: assistant.intent,
      processing_time_ms: assistant.processing_time_ms,
    };
  };

  const startEdit = (m: DialogMessage) => {
    setEditingId(m.id);
    setEditDraft(m.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditDraft('');
  };

  const saveEdit = async () => {
    if (editingId == null) return;
    const cleaned = editDraft.trim();
    if (!cleaned) {
      setError('Текст сообщения не может быть пустым');
      return;
    }
    setEditingBusy(true);
    try {
      await api.patchMessage(editingId, cleaned);
      cancelEdit();
      await load();
      await refreshSessions();
      await loadStats();
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setEditingBusy(false);
    }
  };

  const removeMessage = async (id: number) => {
    if (!window.confirm('Удалить это сообщение?')) return;
    setEditingBusy(true);
    try {
      await api.deleteMessage(id);
      if (editingId === id) cancelEdit();
      await load();
      await refreshSessions();
      await loadStats();
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setEditingBusy(false);
    }
  };

  const clearCurrentSession = async () => {
    if (!sessionId) return;
    if (!window.confirm('Очистить всю историю текущей сессии?')) return;
    await api.clearHistory(sessionId);
    cancelEdit();
    await load();
  };

  return (
    <div className="dialog-layout">
      <SessionSidebar
        sessions={sessions}
        currentSessionId={sessionId}
        onSelect={setSessionId}
        onCreate={newSession}
        onDelete={removeSession}
        onRename={renameSession}
      />
      <section className="chat-main panel chat-main-full">
        <h2 className="sr-only">Диалог</h2>

        <div className="session-toolbar">
          <button type="button" className="btn ghost" onClick={() => void exportJson()}>
            Экспорт JSON
          </button>
          <button type="button" className="btn danger ghost" onClick={() => void clearCurrentSession()}>
            Очистить историю
          </button>
          <input
            type="search"
            className="history-search toolbar-search"
            placeholder="Поиск по сообщениям…"
            value={histFilter}
            onChange={(e) => setHistFilter(e.target.value)}
            aria-label="Поиск по сообщениям"
          />
          {stats ? (
            <span className="toolbar-stats">
              Корпус: {stats.corpus_chunks} фрагм. · Всего сообщений в БД: {stats.messages_total}
            </span>
          ) : null}
        </div>

        {error ? <div className="error">{error}</div> : null}
        <div className="chat-stream">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="welcome-card">
                <div className="welcome-badge">Медицинский ассистент</div>
                <h3>Добро пожаловать</h3>
                <p className="muted welcome-subtitle">
                  Задайте вопрос о симптомах, заболеваниях, специалистах или расшифровке терминов.
                </p>
                <div className="welcome-grid">
                  <div className="welcome-tile">
                    <h4>По симптомам</h4>
                    <p>Кратко опишите самочувствие, чтобы получить ориентир по следующим шагам.</p>
                  </div>
                  <div className="welcome-tile">
                    <h4>По специалистам</h4>
                    <p>Уточните, к какому врачу обращаться и при каких признаках это важно.</p>
                  </div>
                  <div className="welcome-tile">
                    <h4>По терминам</h4>
                    <p>Спросите значение медицинского термина простыми и понятными словами.</p>
                  </div>
                </div>
                <div className="welcome-examples">
                  {[
                    'Что такое гипертония?',
                    'Кашель и температура третий день',
                    'Когда обращаться к кардиологу?',
                    'Расскажи про ВИЧ и СПИД',
                    'Что означает ЭКГ?',
                  ].map((q) => (
                    <button
                      key={q}
                      type="button"
                      className="example-chip"
                      onClick={() => setInput(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            filteredSidebarMessages.map((m) => {
              const shownAssistant =
                m.role === 'assistant' ? getAssistantShown(m, prevUserByAssistantId[m.id]) : null;
              return (
              <div key={m.id} className={`bubble ${m.role}`}>
                <div className="bubble-head">
                  <div className="bubble-label">{m.role === 'user' ? 'Вы' : 'Ассистент'}</div>
                  {m.role === 'user' ? (
                    <div className="bubble-actions">
                      <button
                        type="button"
                        className="btn small ghost chat-action-btn"
                        onClick={() => startEdit(m)}
                        disabled={editingBusy}
                        aria-label="Изменить сообщение"
                        title="Изменить"
                      >
                        ✏
                      </button>
                      <button
                        type="button"
                        className="btn small danger ghost chat-action-btn"
                        onClick={() => void removeMessage(m.id)}
                        disabled={editingBusy}
                        aria-label="Удалить сообщение"
                        title="Удалить"
                      >
                        🗑️
                      </button>
                    </div>
                  ) : m.role === 'assistant' ? (
                    <div className="bubble-actions">
                      <button
                        type="button"
                        className="btn small ghost chat-action-btn"
                        aria-label="Скопировать ответ"
                        title="Скопировать ответ"
                        onClick={() => {
                          const text = shownAssistant?.content || m.content;
                          void navigator.clipboard.writeText(text);
                        }}
                      >
                        ⧉
                      </button>
                    </div>
                  ) : null}
                </div>
                {editingId === m.id && m.role === 'user' ? (
                  <div className="edit-block in-chat-edit">
                    <textarea
                      className="edit-area"
                      value={editDraft}
                      onChange={(e) => setEditDraft(e.target.value)}
                      rows={4}
                      onKeyDown={(e) => {
                        if (e.key === 'Escape') {
                          e.preventDefault();
                          cancelEdit();
                          return;
                        }
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          void saveEdit();
                        }
                      }}
                    />
                    <div className="edit-actions">
                      <button type="button" className="btn small" onClick={() => void saveEdit()} disabled={editingBusy}>
                        Отправить
                      </button>
                      <button type="button" className="btn small ghost" onClick={cancelEdit} disabled={editingBusy}>
                        Отмена
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bubble-body">
                    {m.role === 'user' ? getUserShownText(m) : shownAssistant?.content}
                  </div>
                )}
                {m.role === 'assistant' && m.intent ? (
                  <div className="bubble-meta">
                    {shownAssistant?.intent} · {shownAssistant?.processing_time_ms} мс
                  </div>
                ) : null}
                {m.role === 'user' && m.versions?.length ? (
                  <div className="version-switcher">
                    <button
                      type="button"
                      className="btn small ghost"
                      onClick={() =>
                        setVersionView((prev) => {
                          const cur = prev[m.id] ?? m.versions!.length;
                          const nxt = Math.max(0, cur - 1);
                          return { ...prev, [m.id]: nxt };
                        })
                      }
                      disabled={(versionView[m.id] ?? m.versions.length) <= 0}
                    >
                      ←
                    </button>
                    <span>
                      версия {(versionView[m.id] ?? m.versions.length) + 1} / {m.versions.length + 1}
                    </span>
                    <button
                      type="button"
                      className="btn small ghost"
                      onClick={() =>
                        setVersionView((prev) => {
                          const cur = prev[m.id] ?? m.versions!.length;
                          const nxt = Math.min(m.versions!.length, cur + 1);
                          return { ...prev, [m.id]: nxt };
                        })
                      }
                      disabled={(versionView[m.id] ?? m.versions.length) >= m.versions.length}
                    >
                      →
                    </button>
                  </div>
                ) : null}
                {m.role === 'assistant' && sourcesByMsg[m.id]?.length ? (
                  <details className="corpus-sources">
                    <summary>Фрагменты корпуса (релевантность)</summary>
                    <ul>
                      {sourcesByMsg[m.id].map((s, i) => (
                        <li key={i}>
                          <span className="src-score">{s.score}</span>{' '}
                          {s.meta?.file ? <span className="src-file">{s.meta.file}</span> : null}
                          {s.excerpt ? <pre className="src-excerpt">{s.excerpt}</pre> : null}
                        </li>
                      ))}
                    </ul>
                  </details>
                ) : null}
              </div>
            );
            })
          )}
          <div ref={bottomRef} />
        </div>
        <div className="composer">
          <textarea
            className="composer-input"
            placeholder="Сообщение на русском…"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={sending}
          />
          <button type="button" className="btn primary" onClick={() => void send()} disabled={sending}>
            {sending ? 'Отправка…' : 'Отправить'}
          </button>
        </div>
      </section>
    </div>
  );
}
