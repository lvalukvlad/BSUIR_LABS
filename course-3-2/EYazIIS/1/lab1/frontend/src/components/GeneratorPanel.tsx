import { useState, useEffect } from 'react';
import { api, LemmaEntry } from '../api/client';

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

function GeneratorPanel() {
  const [lemmas, setLemmas] = useState<LemmaEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLemma, setSelectedLemma] = useState<string>('');
  const [selectedCase, setSelectedCase] = useState<string>('');
  const [selectedNumber, setSelectedNumber] = useState<string>('');
  const [selectedGender, setSelectedGender] = useState<string>('');
  const [result, setResult] = useState<{ form: string; info: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLemmas();
  }, []);

  const loadLemmas = async () => {
    try {
      setLoading(true);
      const data = await api.getDictionary();
      setLemmas(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedLemma || !selectedCase || !selectedNumber) {
      setError('Выберите слово, падеж и число');
      return;
    }

    setError(null);
    setResult(null);

    const grammemes: Record<string, string> = {
      падеж: selectedCase,
      число: selectedNumber,
    };

    if (selectedGender) {
      grammemes.род = selectedGender;
    }

    try {
      const response = await api.generateForm(selectedLemma, grammemes);
      setResult({
        form: response.form,
        info: `${selectedCase}, ${selectedNumber}${selectedGender ? ', ' + selectedGender : ''}`,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации');
    }
  };

  const selectedEntry = lemmas.find((l) => l.lemma === selectedLemma);

  return (
    <div className="panel">
      <h2>Генерация словоформ</h2>

      <div className="info-box">
        <p>Выберите слово из словаря и укажите параметры для генерации словоформы.</p>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Загрузка словаря...</div>
      ) : (
        <>
          <div className="form-group">
            <label>Выберите слово (лемму):</label>
            <select
              value={selectedLemma}
              onChange={(e) => {
                setSelectedLemma(e.target.value);
                setResult(null);
              }}
            >
              <option value="">-- Выберите слово --</option>
              {lemmas
                .filter((l) => l.rules && l.rules.length > 0)
                .map((l) => (
                  <option key={l.lemma} value={l.lemma}>
                    {l.lemma} ({l.pos})
                  </option>
                ))}
            </select>
          </div>

          {selectedEntry && (
            <>
              <div className="form-group">
                <label>Доступные правила словоизменения:</label>
                <div className="rules-list">
                  <table>
                    <thead>
                      <tr>
                        <th>Окончание</th>
                        <th>Падеж</th>
                        <th>Число</th>
                        <th>Род</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedEntry.rules.slice(0, 15).map((rule, idx) => (
                        <tr key={idx}>
                          <td><strong>{rule.ending || '(нет)'}</strong></td>
                          <td>{rule.grammemes?.падеж || '-'}</td>
                          <td>{rule.grammemes?.число || '-'}</td>
                          <td>{rule.grammemes?.род || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="form-group">
                <label>Параметры формы:</label>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ fontWeight: 'normal' }}>Падеж:</label>
                    <select
                      value={selectedCase}
                      onChange={(e) => setSelectedCase(e.target.value)}
                    >
                      <option value="">-- Выберите падеж --</option>
                      {CASES.map((c) => (
                        <option key={c.value} value={c.value}>{c.label}</option>
                      ))}
                    </select>
                  </div>
                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ fontWeight: 'normal' }}>Число:</label>
                    <select
                      value={selectedNumber}
                      onChange={(e) => setSelectedNumber(e.target.value)}
                    >
                      <option value="">-- Выберите число --</option>
                      {NUMBERS.map((n) => (
                        <option key={n.value} value={n.value}>{n.label}</option>
                      ))}
                    </select>
                  </div>
                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ fontWeight: 'normal' }}>Род (для ед. числа):</label>
                    <select
                      value={selectedGender}
                      onChange={(e) => setSelectedGender(e.target.value)}
                    >
                      <option value="">-- Не указывать --</option>
                      {GENDERS.map((g) => (
                        <option key={g.value} value={g.value}>{g.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={handleGenerate}
                disabled={!selectedLemma || !selectedCase || !selectedNumber}
              >
                Сгенерировать форму
              </button>

              {result && (
                <div style={{ marginTop: '24px', padding: '20px', background: '#e8f8f5', borderRadius: '8px' }}>
                  <h3 style={{ marginBottom: '12px', color: '#27ae60' }}>Результат:</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2c3e50' }}>
                    {result.form}
                  </div>
                  <div style={{ marginTop: '8px', color: '#666' }}>
                    Параметры: {result.info}
                  </div>
                  <div style={{ marginTop: '8px', color: '#888', fontSize: '0.9rem' }}>
                    Основа: {selectedEntry.stem}
                  </div>
                </div>
              )}
            </>
          )}

          {lemmas.length === 0 && (
            <div className="empty-state">
              Словарь пуст. Добавьте слова через "Анализ текста" или вручную.
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default GeneratorPanel;
