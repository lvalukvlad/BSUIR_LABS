import { useState, useRef } from 'react';
import { api, AnalyzeResult } from '../api/client';

function AnalysisPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeFile(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка анализа файла');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.txt') || droppedFile.name.endsWith('.rtf'))) {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Поддерживаются только файлы TXT и RTF');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="panel">
      <h2>Анализ текста</h2>

      <div className="info-box">
        <p>Загрузите текстовый файл (TXT или RTF) для автоматического анализа и пополнения словаря.</p>
      </div>

      {error && <div className="error">{error}</div>}

      <div
        className="upload-area"
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.rtf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <p>Перетащите файл сюда или нажмите для выбора</p>
        <p style={{ fontSize: '0.875rem', color: '#999' }}>Форматы: TXT, RTF</p>
      </div>

      {file && (
        <div className="file-info">
          Выбран файл: {file.name} ({(file.size / 1024).toFixed(1)} КБ)
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading ? 'Анализ...' : 'Проанализировать файл'}
        </button>
      </div>

      {result && (
        <div className="results">
          <h3>Результаты анализа</h3>
          <div className="result-item">
            <strong>Всего токенов:</strong> {result.total_tokens}
          </div>
          <div className="result-item">
            <strong>Уникальных лемм:</strong> {result.unique_lemmas}
          </div>
          <div className="result-item">
            <strong>Время обработки:</strong> {result.processing_time_ms} мс
          </div>
          <div className="result-item">
            <strong>Файл:</strong> {result.file_info.name} ({result.file_info.format})
          </div>

          <h4 style={{ marginTop: '16px', marginBottom: '8px' }}>Найденные леммы:</h4>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Лемма</th>
                  <th>Часть речи</th>
                  <th>Частота</th>
                </tr>
              </thead>
              <tbody>
                {result.lemmas.map((lemma) => (
                  <tr key={lemma.lemma}>
                    <td><strong>{lemma.lemma}</strong></td>
                    <td>{lemma.pos}</td>
                    <td>{lemma.frequency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalysisPanel;
