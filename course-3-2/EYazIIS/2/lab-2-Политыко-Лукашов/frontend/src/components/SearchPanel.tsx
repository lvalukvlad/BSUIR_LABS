import { useState } from 'react';
import { api, ConcordanceItem, Document } from '../api/client';

function SearchPanel() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [concordance, setConcordance] = useState<ConcordanceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchType, setSearchType] = useState<'search' | 'concordance'>('search');
  const [concordanceTime, setConcordanceTime] = useState<number | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [viewDocLoading, setViewDocLoading] = useState(false);
  const [highlightWord, setHighlightWord] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      if (searchType === 'search') {
        const startTime = performance.now();
        const results = await api.search(query);
        setSearchTime(performance.now() - startTime);
        setSearchResults(results.results || []);
      } else {
        const startTime = performance.now();
        const results = await api.getConcordance(query);
        const elapsed = performance.now() - startTime;
        setConcordanceTime(elapsed);
        setConcordance(results.concordance || []);
      }
    } catch (err) {
      setError('Ошибка поиска');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleViewDocument = async (docId: string, keyword: string) => {
    try {
      setViewDocLoading(true);
      const doc = await api.getDocument(docId);
      setSelectedDoc(doc);
      setHighlightWord(keyword);
    } catch (err) {
      setError('Не удалось загрузить документ');
    } finally {
      setViewDocLoading(false);
    }
  };

  const closeDocument = () => {
    setSelectedDoc(null);
    setHighlightWord('');
  };

  const renderHighlightedContent = (content: string, word: string) => {
    if (!word) return content;
    const regex = new RegExp(`(${word})`, 'gi');
    const parts = content.split(regex);
    return parts.map((part, i) => 
      regex.test(part) ? <span key={i} className="highlight">{part}</span> : part
    );
  };

  return (
    <div className="panel">
      <h2>Поиск по корпусу</h2>

      <div className="search-type-tabs">
        <button
          className={searchType === 'search' ? 'active' : ''}
          onClick={() => setSearchType('search')}
        >
          Простой поиск
        </button>
        <button
          className={searchType === 'concordance' ? 'active' : ''}
          onClick={() => setSearchType('concordance')}
        >
          Конкорданс
        </button>
      </div>

      <div className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите слово для поиска..."
          className="search-input"
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {searchType === 'search' && (
        <div className="search-results">
          <h3>Результаты поиска ({searchResults.length}){searchTime !== null && <span className="time-info"> — {searchTime.toFixed(0)} мс</span>}</h3>
          {searchResults.length === 0 ? (
            <p>Введите запрос и нажмите "Найти"</p>
          ) : (
            <ul className="results-list">
              {searchResults.map((result, idx) => (
                <li key={idx} className="result-item">
                  <div className="result-doc">{result.document_title}</div>
                  <div className="result-context">{result.context}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {searchType === 'concordance' && (
        <div className="concordance-results">
          <h3>Конкорданс ({concordance.length}){concordanceTime !== null && <span className="time-info"> — {concordanceTime.toFixed(0)} мс</span>}</h3>
          {concordance.length === 0 ? (
            <p>Введите слово и нажмите "Найти"</p>
          ) : (
            <ul className="results-list">
              {concordance.map((item, idx) => (
                <li key={idx} className="result-item">
                  <div className="result-doc">{item.document_title}</div>
                  <div className="result-context">
                    {item.left} <span className="highlight">{item.keyword}</span> {item.right}
                  </div>
                  <button 
                    className="view-btn"
                    onClick={() => handleViewDocument(item.document_id, item.keyword)}
                    disabled={viewDocLoading}
                  >
                    Просмотреть
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {selectedDoc && (
        <div className="document-view">
          <h3>{selectedDoc.title}</h3>
          <div className="metadata">
            <p><strong>Тип:</strong> {selectedDoc.metadata.text_type}</p>
            <p><strong>Автор:</strong> {selectedDoc.metadata.author || '-'}</p>
            <p><strong>Жанр:</strong> {selectedDoc.metadata.genre || '-'}</p>
            <p><strong>Дата:</strong> {selectedDoc.metadata.date || '-'}</p>
            <p><strong>Слов:</strong> {selectedDoc.metadata.word_count}</p>
            <p><strong>Символов:</strong> {selectedDoc.metadata.char_count}</p>
            <p><strong>Создан:</strong> {selectedDoc.metadata.created_at}</p>
          </div>
          <div className="content">
            <pre>{renderHighlightedContent(selectedDoc.content, highlightWord)}</pre>
          </div>
          <button onClick={closeDocument}>Закрыть</button>
        </div>
      )}
    </div>
  );
}

export default SearchPanel;
