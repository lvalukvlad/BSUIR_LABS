export type CorpusSource = {
  score: number;
  meta: { file?: string; section_title?: string; length?: number };
  excerpt?: string;
};

export type DialogMessage = {
  id: number;
  session_id?: string;
  role: string;
  content: string;
  intent: string;
  processing_time_ms: number;
  edit_version?: number;
  versions?: {
    user: string;
    assistant: string;
    intent?: string;
    processing_time_ms?: number;
    edited_at?: string;
  }[];
  created_at: string;
  updated_at: string;
  sources?: CorpusSource[];
};

export type DialogSessionInfo = {
  id: string;
  title: string;
  context: Record<string, unknown>;
  message_count: number;
  created_at: string;
  updated_at: string;
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async sendMessage(text: string, sessionId: string) {
    const res = await fetch('/api/dialog/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, session_id: sessionId }),
    });
    return json<{
      user_message: DialogMessage;
      assistant_message: DialogMessage;
      intent: string;
      processing_time_ms: number;
      sources: CorpusSource[];
      session_context: Record<string, unknown>;
    }>(res);
  },

  async getHistory(sessionId: string) {
    const q = new URLSearchParams({ session_id: sessionId });
    const res = await fetch(`/api/dialog/history?${q}`);
    return json<{ messages: DialogMessage[]; session_id: string }>(res);
  },

  async patchMessage(id: number, content: string) {
    const res = await fetch(`/api/dialog/messages/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    return json<DialogMessage>(res);
  },

  async deleteMessage(id: number) {
    const res = await fetch(`/api/dialog/messages/${id}`, { method: 'DELETE' });
    return json<{ ok: boolean; id: number }>(res);
  },

  async clearHistory(sessionId: string) {
    const q = new URLSearchParams({ session_id: sessionId });
    const res = await fetch(`/api/dialog/history?${q}`, { method: 'DELETE' });
    return json<{ ok: boolean; session_id: string }>(res);
  },

  async exportSession(sessionId: string) {
    const q = new URLSearchParams({ session_id: sessionId });
    const res = await fetch(`/api/dialog/export?${q}`);
    return json<{
      session_id: string;
      title: string;
      context: Record<string, unknown>;
      messages: DialogMessage[];
      exported_at: string;
    }>(res);
  },

  async listSessions() {
    const res = await fetch('/api/sessions');
    return json<{ sessions: DialogSessionInfo[] }>(res);
  },

  async createSession(title?: string) {
    const res = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || null }),
    });
    return json<DialogSessionInfo>(res);
  },

  async renameSession(sessionId: string, title: string) {
    const res = await fetch(`/api/sessions/${sessionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    return json<DialogSessionInfo>(res);
  },

  async deleteSession(sessionId: string) {
    const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
    return json<{ ok: boolean }>(res);
  },

  async getStats() {
    const res = await fetch('/api/stats');
    return json<{
      messages_total: number;
      sessions_total: number;
      corpus_chunks: number;
      corpus_indexed: boolean;
      database_path: string;
    }>(res);
  },

  async getHelp() {
    const res = await fetch('/api/help');
    return json<{
      title: string;
      description: string;
      sections: { id: string; title: string; content: string }[];
      stack?: string[];
    }>(res);
  },

  async getTerms() {
    const res = await fetch('/api/terms');
    return json<{
      title: string;
      terms: { term: string; definition: string }[];
    }>(res);
  },
};
