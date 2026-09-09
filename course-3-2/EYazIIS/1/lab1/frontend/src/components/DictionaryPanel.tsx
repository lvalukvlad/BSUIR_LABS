import { useState, useEffect, useCallback } from 'react';
import { api, LemmaEntry } from '../api/client';

const POS_OPTIONS = [
  'существительное',
  'прилагательное', 
  'глагол',
  'наречие',
  'местоимение',
  'числительное',
  'предлог',
  'союз',
  'частица',
  'междометие',
];

const CASES = [
  { value: 'именительный', label: 'Именительный' },
  { value: 'родительный', label: 'Родительный' },
  { value: 'дательный', label: 'Дательный' },
  { value: 'винительный', label: 'Винительный' },
  { value: 'творительный', label: 'Творительный' },
  { value: 'предложный', label: 'Предложный' },
];

const NUMBERS = [
  { value: 'единственное', label: 'Единственное' },
  { value: 'множественное', label: 'Множественное' },
];

const GENDERS = [
  { value: 'мужской', label: 'Мужской' },
  { value: 'женский', label: 'Женский' },
  { value: 'средний', label: 'Средний' },
];

function DictionaryPanel() {
  const [lemmas, setLemmas] = useState<LemmaEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [posFilter, setPosFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingLemma, setEditingLemma] = useState<LemmaEntry | null>(null);
  const [showRulesModal, setShowRulesModal] = useState(false);
  const [rulesLemma, setRulesLemma] = useState<LemmaEntry | null>(null);
  const [newRule, setNewRule] = useState({ ending: '', grammemes: { падеж: '', число: '', род: '' } });
  const [formData, setFormData] = useState({
    lemma: '',
    stem: '',
    pos: '',
    frequency: 0,
  });

  const loadDictionary = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDictionary(search || undefined, posFilter || undefined);
      setLemmas(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки словаря');
    } finally {
      setLoading(false);
    }
  }, [search, posFilter]);

  useEffect(() => {
    loadDictionary();
  }, [loadDictionary]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadDictionary();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, loadDictionary]);

  const handleAdd = () => {
    setEditingLemma(null);
    setFormData({
      lemma: '',
      stem: '',
      pos: '',
      frequency: 0,
    });
    setShowModal(true);
  };

  const handleEdit = (lemma: LemmaEntry) => {
    setEditingLemma(lemma);
    setFormData({
      lemma: lemma.lemma,
      stem: lemma.stem,
      pos: lemma.pos,
      frequency: lemma.frequency,
    });
    setShowModal(true);
  };

  const handleRulesClick = (lemma: LemmaEntry) => {
    setRulesLemma(lemma);
    setNewRule({ ending: '', grammemes: { падеж: '', число: '', род: '' } });
    setShowRulesModal(true);
  };

  const handleAddRule = async () => {
    if (!rulesLemma || !newRule.ending) return;
    try {
      await api.addRule(rulesLemma.lemma, {
        ending: newRule.ending,
        grammemes: Object.fromEntries(
          Object.entries(newRule.grammemes).filter(([_, v]) => v !== '')
        ),
      });
      const updated = await api.getLemma(rulesLemma.lemma);
      setRulesLemma(updated);
      setNewRule({ ending: '', grammemes: { падеж: '', число: '', род: '' } });
      loadDictionary();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка добавления правила');
    }
  };

  const handleDeleteRule = async (index: number) => {
    if (!rulesLemma) return;
    try {
      await api.deleteRule(rulesLemma.lemma, index);
      const updated = await api.getLemma(rulesLemma.lemma);
      setRulesLemma(updated);
      loadDictionary();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления правила');
    }
  };

  const handleDelete = async (lemma: string) => {
    if (!confirm(`Удалить слово "${lemma}"?`)) return;
    try {
      await api.deleteLemma(lemma);
      loadDictionary();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      const entry: LemmaEntry = {
        lemma: formData.lemma,
        stem: formData.stem || formData.lemma,
        pos: formData.pos,
        rules: editingLemma?.rules || [],
        frequency: formData.frequency,
        meta: null,
      };

      if (editingLemma) {
        await api.updateLemma(editingLemma.lemma, entry);
      } else {
        await api.addLemma(entry);
      }

      setShowModal(false);
      loadDictionary();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения');
    }
  };

  const handleExport = async (format: 'json' | 'txt') => {
    try {
      const data = await api.exportDictionary(format);
      if (format === 'txt' && data.content) {
        const blob = new Blob([data.content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dictionary.txt';
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dictionary.json';
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка экспорта');
    }
  };

  return (
    <div className="panel">
      <h2>Словарь</h2>

      {error && <div className="error">{error}</div>}

      <div className="search-bar">
        <input
          type="text"
          placeholder="Поиск (введите буквы для динамического поиска)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={posFilter} onChange={(e) => setPosFilter(e.target.value)}>
          <option value="">Все части речи</option>
          {POS_OPTIONS.map((pos) => (
            <option key={pos} value={pos}>{pos}</option>
          ))}
        </select>
        <button className="btn btn-primary" onClick={handleAdd}>
          Добавить слово
        </button>
        <button className="btn btn-secondary" onClick={() => handleExport('txt')}>
          Экспорт TXT
        </button>
        <button className="btn btn-secondary" onClick={() => handleExport('json')}>
          Экспорт JSON
        </button>
      </div>

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : lemmas.length === 0 ? (
        <div className="empty-state">
          {search || posFilter ? 'Слова не найдены' : 'Словарь пуст. Добавьте слова или загрузите файл для анализа.'}
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Лемма</th>
                <th>Основа</th>
                <th>Часть речи</th>
                <th>Частота</th>
                <th>Правила</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {lemmas.map((item) => (
                <tr key={item.lemma}>
                  <td><strong>{item.lemma}</strong></td>
                  <td>{item.stem}</td>
                  <td>{item.pos}</td>
                  <td>{item.frequency}</td>
                  <td>
                    <button className="btn btn-secondary" onClick={() => handleRulesClick(item)}>
                      {item.rules?.length || 0} правил
                    </button>
                  </td>
                  <td className="actions">
                    <button className="btn btn-primary" onClick={() => handleEdit(item)}>
                      Изменить
                    </button>
                    <button className="btn btn-danger" onClick={() => handleDelete(item.lemma)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingLemma ? 'Редактирование слова' : 'Добавление слова'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Лемма (начальная форма) *</label>
                <input
                  type="text"
                  value={formData.lemma}
                  onChange={(e) => setFormData({ ...formData, lemma: e.target.value })}
                  required
                  disabled={!!editingLemma}
                />
              </div>
              <div className="form-group">
                <label>Основа слова</label>
                <input
                  type="text"
                  value={formData.stem}
                  onChange={(e) => setFormData({ ...formData, stem: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Часть речи</label>
                <select
                  value={formData.pos}
                  onChange={(e) => setFormData({ ...formData, pos: e.target.value })}
                  required
                >
                  <option value="">Выберите часть речи</option>
                  {POS_OPTIONS.map((pos) => (
                    <option key={pos} value={pos}>{pos}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Частота</label>
                <input
                  type="number"
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: parseInt(e.target.value) || 0 })}
                  min="0"
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Отмена
                </button>
                <button type="submit" className="btn btn-success">
                  {editingLemma ? 'Сохранить' : 'Добавить'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showRulesModal && rulesLemma && (
        <div className="modal-overlay" onClick={() => setShowRulesModal(false)}>
          <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
            <h3>Управление правилами словоизменения: <strong>{rulesLemma.lemma}</strong></h3>
            <p style={{ marginBottom: '16px', color: '#666' }}>
              Основа: <strong>{rulesLemma.stem}</strong> | Часть речи: <strong>{rulesLemma.pos}</strong>
            </p>

            <div style={{ marginBottom: '24px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
              <h4>Добавить новое правило</h4>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '12px' }}>
                <div style={{ flex: 1, minWidth: '120px' }}>
                  <label style={{ fontWeight: 'normal', fontSize: '0.9rem' }}>Окончание:</label>
                  <input
                    type="text"
                    value={newRule.ending}
                    onChange={(e) => setNewRule({ ...newRule, ending: e.target.value })}
                    placeholder="напр. -ами"
                    style={{ width: '100%', marginTop: '4px' }}
                  />
                </div>
                <div style={{ flex: 1, minWidth: '120px' }}>
                  <label style={{ fontWeight: 'normal', fontSize: '0.9rem' }}>Падеж:</label>
                  <select
                    value={newRule.grammemes.падеж}
                    onChange={(e) => setNewRule({ ...newRule, grammemes: { ...newRule.grammemes, падеж: e.target.value } })}
                    style={{ width: '100%', marginTop: '4px' }}
                  >
                    <option value="">Не указан</option>
                    {CASES.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: 1, minWidth: '120px' }}>
                  <label style={{ fontWeight: 'normal', fontSize: '0.9rem' }}>Число:</label>
                  <select
                    value={newRule.grammemes.число}
                    onChange={(e) => setNewRule({ ...newRule, grammemes: { ...newRule.grammemes, число: e.target.value } })}
                    style={{ width: '100%', marginTop: '4px' }}
                  >
                    <option value="">Не указано</option>
                    {NUMBERS.map((n) => (
                      <option key={n.value} value={n.value}>{n.label}</option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: 1, minWidth: '120px' }}>
                  <label style={{ fontWeight: 'normal', fontSize: '0.9rem' }}>Род:</label>
                  <select
                    value={newRule.grammemes.род}
                    onChange={(e) => setNewRule({ ...newRule, grammemes: { ...newRule.grammemes, род: e.target.value } })}
                    style={{ width: '100%', marginTop: '4px' }}
                  >
                    <option value="">Не указан</option>
                    {GENDERS.map((g) => (
                      <option key={g.value} value={g.value}>{g.label}</option>
                    ))}
                  </select>
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                  <button
                    type="button"
                    className="btn btn-success"
                    onClick={handleAddRule}
                    disabled={!newRule.ending}
                  >
                    Добавить
                  </button>
                </div>
              </div>
            </div>

            <h4>Существующие правила ({rulesLemma.rules?.length || 0})</h4>
            <div className="rules-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {(!rulesLemma.rules || rulesLemma.rules.length === 0) ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                  Правила отсутствуют. Добавьте правила выше.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {rulesLemma.rules.map((rule, idx) => {
                    const exampleForm = rulesLemma.stem + rule.ending;
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: '16px',
                          background: '#fff',
                          border: '1px solid #ddd',
                          borderRadius: '8px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#2c3e50' }}>
                            {rulesLemma.stem} + <span style={{ color: '#e74c3c' }}>{rule.ending || '(пусто)'}</span> = <span style={{ color: '#27ae60' }}>{exampleForm}</span>
                          </div>
                          <div style={{ marginTop: '8px', color: '#666', fontSize: '0.9rem' }}>
                            {rule.grammemes?.падеж && <span>Падеж: <strong>{rule.grammemes.падеж}</strong></span>}
                            {rule.grammemes?.число && <span style={{ marginLeft: '12px' }}>Число: <strong>{rule.grammemes.число}</strong></span>}
                            {rule.grammemes?.род && <span style={{ marginLeft: '12px' }}>Род: <strong>{rule.grammemes.род}</strong></span>}
                            {!rule.grammemes?.падеж && !rule.grammemes?.число && !rule.grammemes?.род && <span style={{ color: '#888' }}>Без морфологических признаков</span>}
                          </div>
                        </div>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDeleteRule(idx)}
                        >
                          Удалить
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="form-actions" style={{ marginTop: '20px' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setShowRulesModal(false)}>
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DictionaryPanel;
