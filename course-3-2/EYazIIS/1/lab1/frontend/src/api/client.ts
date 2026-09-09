const API_BASE = 'http://127.0.0.1:8000/api';

export interface MorphRule {
  ending: string;
  grammemes: Record<string, string>;
}

export interface LemmaEntry {
  lemma: string;
  stem: string;
  pos: string;
  rules: MorphRule[];
  frequency: number;
  meta: Record<string, unknown> | null;
}

export interface AnalyzeResult {
  total_tokens: number;
  unique_lemmas: number;
  lemmas: LemmaEntry[];
  processing_time_ms: number;
  file_info: { name: string; format: string };
}

export const api = {
  async getDictionary(search?: string, pos?: string): Promise<LemmaEntry[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (pos) params.append('pos', pos);
    const url = `${API_BASE}/dictionary${params.toString() ? '?' + params : ''}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch dictionary');
    return res.json();
  },

  async getLemma(lemma: string): Promise<LemmaEntry> {
    const res = await fetch(`${API_BASE}/dictionary-item?lemma=${encodeURIComponent(lemma)}`);
    if (!res.ok) throw new Error('Lemma not found');
    return res.json();
  },

  async addLemma(entry: LemmaEntry): Promise<LemmaEntry> {
    const res = await fetch(`${API_BASE}/dictionary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add lemma');
    }
    return res.json();
  },

  async updateLemma(lemma: string, entry: LemmaEntry): Promise<LemmaEntry> {
    const res = await fetch(`${API_BASE}/dictionary?lemma=${encodeURIComponent(lemma)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update lemma');
    }
    return res.json();
  },

  async deleteLemma(lemma: string): Promise<void> {
    const res = await fetch(`${API_BASE}/dictionary?lemma=${encodeURIComponent(lemma)}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete lemma');
    }
  },

  async exportDictionary(format: 'json' | 'txt' = 'json'): Promise<{ format: string; total?: number; content?: string; entries?: LemmaEntry[] }> {
    const res = await fetch(`${API_BASE}/dictionary/export?format=${format}`);
    if (!res.ok) throw new Error('Failed to export dictionary');
    return res.json();
  },

  async analyzeFile(file: File): Promise<AnalyzeResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to analyze file');
    }
    return res.json();
  },

  async generateForm(lemma: string, grammemes: Record<string, string>): Promise<{ form: string }> {
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lemma, grammemes }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate form');
    }
    return res.json();
  },

  async healthCheck(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('API not available');
    return res.json();
  },

  async updateRules(lemma: string, rules: MorphRule[]): Promise<LemmaEntry> {
    const res = await fetch(`${API_BASE}/dictionary/${encodeURIComponent(lemma)}/rules`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rules),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update rules');
    }
    return res.json();
  },

  async addRule(lemma: string, rule: MorphRule): Promise<{ success: boolean; added: MorphRule; total_rules: number }> {
    const res = await fetch(`${API_BASE}/dictionary/${encodeURIComponent(lemma)}/rules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rule),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add rule');
    }
    return res.json();
  },

  async deleteRule(lemma: string, ruleIndex: number): Promise<{ success: boolean; deleted: MorphRule; remaining_rules: number }> {
    const res = await fetch(`${API_BASE}/dictionary/${encodeURIComponent(lemma)}/rules/${ruleIndex}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete rule');
    }
    return res.json();
  },
};
