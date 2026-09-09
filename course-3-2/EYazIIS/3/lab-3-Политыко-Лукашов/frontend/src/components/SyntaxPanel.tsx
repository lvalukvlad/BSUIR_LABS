import { useState, useEffect } from 'react';
import { api, Document, AnalysisResult, Sentence, Token, RelationsResult, DependencyTree, ConstituencyTree } from '../api/client';
import TreeVisualization from './TreeVisualization';

const SYNTAX_ROLES = [
  { value: '', label: '—' },
  { value: 'подлежащее', label: 'Подлежащее' },
  { value: 'сказуемое', label: 'Сказуемое' },
  { value: 'дополнение', label: 'Дополнение' },
  { value: 'определение', label: 'Определение' },
  { value: 'обстоятельство', label: 'Обстоятельство' },
];

const RELATION_TYPES: Record<string, string> = {
  'subject-predicate': 'Подлежащее → Сказуемое',
  'predicate-object': 'Сказуемое → Дополнение',
  'attribute-noun': 'Определение → Существительное',
  'adverbial-predicate': 'Обстоятельство → Сказуемое',
};

function SyntaxPanel() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [directText, setDirectText] = useState('');
  const [directAnalyzing, setDirectAnalyzing] = useState(false);
  const [directAnalysis, setDirectAnalysis] = useState<AnalysisResult | null>(null);
  const [relations, setRelations] = useState<RelationsResult | null>(null);
  const [showRelations, setShowRelations] = useState(false);
  const [editingDoc, setEditingDoc] = useState<Document | null>(null);
  const [editContent, setEditContent] = useState('');
  const [savingDoc, setSavingDoc] = useState(false);
  const [relationsPage, setRelationsPage] = useState(0);
  const [sentenceRelationsPage, setSentenceRelationsPage] = useState<Record<number, number>>({});
  const [dependencyTrees, setDependencyTrees] = useState<DependencyTree[]>([]);
  const [constituencyTrees, setConstituencyTrees] = useState<ConstituencyTree[]>([]);
  const [showTrees, setShowTrees] = useState(false);
  const [loadingTrees, setLoadingTrees] = useState(false);
  const RELATIONS_PER_PAGE = 15;
  const RELATIONS_PER_PAGE_SMALL = 4;

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.getDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      setError('Не удалось загрузить документы');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await api.loadFile(file);
      await loadDocuments();
    } catch (err) {
      setError('Не удалось загрузить файл');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Удалить документ?')) return;
    try {
      await api.deleteDocument(docId);
      await loadDocuments();
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
        setAnalysis(null);
        setRelations(null);
        setRelationsPage(0);
        setEditingDoc(null);
      }
    } catch (err) {
      setError('Не удалось удалить документ');
    }
  };

  const handleAnalyze = async (docId: string) => {
    try {
      setAnalyzing(true);
      const result = await api.analyzeDocument(docId);
      setAnalysis(result);
      const rels = await api.getDocumentRelations(docId);
      setRelations(rels);
      setRelationsPage(0);
      
      setLoadingTrees(true);
      try {
        const depResult = await api.getDependencyTree(docId);
        const constResult = await api.getConstituencyTree(docId);
        setDependencyTrees(depResult.trees || []);
        setConstituencyTrees(constResult.trees || []);
      } catch {
        console.error('Failed to load trees');
      } finally {
        setLoadingTrees(false);
      }
    } catch (err) {
      setError('Не удалось проанализировать документ');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleViewDocument = async (docId: string) => {
    try {
      const res = await fetch(`/api/documents/${docId}`);
      const doc = await res.json();
      setSelectedDoc(doc);
      setEditContent(doc.content);
    } catch (err) {
      setError('Не удалось загрузить документ');
    }
  };

  const handleEditStart = () => {
    if (selectedDoc) {
      setEditingDoc(selectedDoc);
      setEditContent(selectedDoc.content);
    }
  };

  const handleEditCancel = () => {
    setEditingDoc(null);
    setEditContent('');
  };

  const handleEditSave = async () => {
    if (!selectedDoc) return;
    try {
      setSavingDoc(true);
      const result = await api.updateDocument(selectedDoc.id, editContent);
      setEditingDoc(null);
      setAnalysis(result);
      const rels = await api.getDocumentRelations(selectedDoc.id);
      setRelations(rels);
      setRelationsPage(0);
      await loadDocuments();
      const res = await fetch(`/api/documents/${selectedDoc.id}`);
      const doc = await res.json();
      setSelectedDoc(doc);
    } catch (err) {
      setError('Не удалось сохранить документ');
    } finally {
      setSavingDoc(false);
    }
  };
  const handleExportJson = async (docId: string, docTitle: string) => {
    try {
      const result = await api.getDocumentAnalysis(docId);
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${docTitle}_analysis.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Не удалось экспортировать JSON');
    }
  };

  const handleDirectAnalyze = async () => {
    if (!directText.trim()) return;
    try {
      setDirectAnalyzing(true);
      const [analysisResult, treeResult] = await Promise.all([
        api.analyzeText(directText),
        api.analyzeTextTrees(directText),
      ]);
      setDirectAnalysis(analysisResult);
      setDependencyTrees(treeResult.dependency_trees || []);
      setConstituencyTrees(treeResult.constituency_trees || []);
    } catch (err) {
      setError('Не удалось проанализировать текст');
    } finally {
      setDirectAnalyzing(false);
    }
  };

  const handleRoleChange = async (docId: string, sentenceId: number, tokenId: number, newRole: string) => {
    const roleLabel = SYNTAX_ROLES.find(r => r.value === newRole)?.label || '';
    try {
      await api.updateToken(docId, sentenceId, tokenId, newRole, roleLabel);
      const result = await api.getDocumentAnalysis(docId);
      setAnalysis(result);
    } catch (err) {
      setError('Не удалось обновить роль');
    }
  };

  const getRoleClass = (role: string) => {
    switch (role) {
      case 'подлежащее': return 'subject';
      case 'сказуемое': return 'predicate';
      case 'дополнение': return 'object';
      case 'определение': return 'attribute';
      case 'обстоятельство': return 'adverbial';
      default: return '';
    }
  };

  const getRelationClass = (type: string) => {
    switch (type) {
      case 'subject-predicate': return 'relation-subject';
      case 'predicate-object': return 'relation-object';
      case 'attribute-noun': return 'relation-attribute';
      case 'adverbial-predicate': return 'relation-adverbial';
      default: return '';
    }
  };

  const renderSentenceTable = (sentence: Sentence, docId?: string) => {
    const sentenceRelations = relations?.relations.filter(r => r.sentence_index === sentence.sentence_index) || [];
    const currentPage = sentenceRelationsPage[sentence.sentence_index] || 0;
    const totalPages = Math.ceil(sentenceRelations.length / RELATIONS_PER_PAGE_SMALL);
    const pageRelations = sentenceRelations.slice(currentPage * RELATIONS_PER_PAGE_SMALL, (currentPage + 1) * RELATIONS_PER_PAGE_SMALL);
    
    return (
      <div key={sentence.sentence_index} className="sentence-section">
        <div className="sentence-header">
          <h4>Предложение {sentence.sentence_index}</h4>
          <span>{sentence.tokens.length} слов</span>
        </div>
        <p style={{ marginBottom: '1rem', color: '#666', fontStyle: 'italic' }}>
          "{sentence.sentence_text}"
        </p>
        
        {sentenceRelations.length > 0 && (
          <div className="sentence-relations">
            <h5>Синтаксические связи:</h5>
            <table className="sentence-relations-table">
              <thead>
                <tr>
                  <th>№</th>
                  <th>От кого</th>
                  <th>Куда</th>
                  <th>Тип связи</th>
                </tr>
              </thead>
              <tbody>
                {pageRelations.map((rel, idx) => (
                  <tr key={idx}>
                    <td>{currentPage * RELATIONS_PER_PAGE + idx + 1}</td>
                    <td>{rel.relation.from_token_text}</td>
                    <td>{rel.relation.to_token_text}</td>
                    <td>
                      <span className={`relation-badge ${getRelationClass(rel.relation.relation_type)}`}>
                        {RELATION_TYPES[rel.relation.relation_type] || rel.relation.relation_name}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="sentence-pagination">
                <button 
                  onClick={() => setSentenceRelationsPage(p => ({...p, [sentence.sentence_index]: Math.max(0, currentPage - 1)}))}
                  disabled={currentPage === 0}
                >
                  ←
                </button>
                <span>{currentPage + 1}/{totalPages}</span>
                <button 
                  onClick={() => setSentenceRelationsPage(p => ({...p, [sentence.sentence_index]: Math.min(totalPages - 1, currentPage + 1)}))}
                  disabled={currentPage >= totalPages - 1}
                >
                  →
                </button>
              </div>
            )}
          </div>
        )}
        
        <table className="results-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Слово</th>
              <th>Часть речи</th>
              <th>Лемма</th>
              <th>Грамматика</th>
              <th>Член предложения</th>
            </tr>
          </thead>
          <tbody>
            {sentence.tokens.map((token: Token, tokenIdx: number) => {
              if (!token.pos || token.pos === 'PUNCT') return null;
              return (
                <tr key={tokenIdx}>
                  <td>{token.position}</td>
                  <td className="token">{token.token_text}</td>
                  <td className="pos">{token.pos_name || token.pos}</td>
                  <td>{token.lemma}</td>
                  <td className="grammemes">
                    {[token.case_name, token.number_name, token.gender_name].filter(Boolean).join(', ')}
                  </td>
                  <td>
                    {docId ? (
                      <select
                        className="role-select"
                        value={token.syntax_role}
                        onChange={(e) => handleRoleChange(docId, sentence.id, token.id, e.target.value)}
                      >
                        {SYNTAX_ROLES.map((role) => (
                          <option key={role.value} value={role.value}>
                            {role.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className={`syntax-role ${getRoleClass(token.syntax_role)}`}>
                        {token.syntax_role_name || '—'}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRelationsPanel = () => {
    if (!relations) return null;
    
    const totalPages = Math.ceil(relations.relations.length / RELATIONS_PER_PAGE);
    const startIdx = relationsPage * RELATIONS_PER_PAGE;
    const pageRelations = relations.relations.slice(startIdx, startIdx + RELATIONS_PER_PAGE);
    
    return (
      <div className="relations-panel">
        <h3>Синтаксические связи</h3>
        {relations.relations.length === 0 ? (
          <p>Связи не найдены</p>
        ) : (
          <>
            <table className="relations-table">
              <thead>
                <tr>
                  <th>№</th>
                  <th>От кого</th>
                  <th>Куда</th>
                  <th>Тип связи</th>
                </tr>
              </thead>
              <tbody>
                {pageRelations.map((rel, idx) => (
                  <tr key={startIdx + idx}>
                    <td>{startIdx + idx + 1}</td>
                    <td>{rel.relation.from_token_text}</td>
                    <td>{rel.relation.to_token_text}</td>
                    <td>
                      <span className={`relation-badge ${getRelationClass(rel.relation.relation_type)}`}>
                        {RELATION_TYPES[rel.relation.relation_type] || rel.relation.relation_name}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  onClick={() => setRelationsPage(p => Math.max(0, p - 1))}
                  disabled={relationsPage === 0}
                >
                  Предыдущая
                </button>
                <span>{relationsPage + 1} / {totalPages}</span>
                <button 
                  onClick={() => setRelationsPage(p => Math.min(totalPages - 1, p + 1))}
                  disabled={relationsPage >= totalPages - 1}
                >
                  Следующая
                </button>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  const renderStatistics = (stats: AnalysisResult['statistics'], analysisTime?: number) => {
    return (
      <div className="statistics">
        <h3>Статистика</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <h4>Общая информация</h4>
            <ul>
              <li><span>Предложений:</span> <strong>{stats.total_sentences}</strong></li>
              <li><span>Слов:</span> <strong>{stats.total_tokens}</strong></li>
              {analysisTime !== undefined && (
                <li><span>Время анализа:</span> <strong>{analysisTime} мс</strong></li>
              )}
            </ul>
          </div>
          <div className="stat-item">
            <h4>Части речи</h4>
            <ul>
              {Object.entries(stats.pos_distribution)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([pos, count]) => (
                  <li key={pos}>
                    <span>{pos}</span> <strong>{count}</strong>
                  </li>
                ))}
            </ul>
          </div>
          <div className="stat-item">
            <h4>Члены предложения</h4>
            <ul>
              {Object.entries(stats.syntax_role_distribution)
                .sort((a, b) => b[1] - a[1])
                .map(([role, count]) => (
                  <li key={role}>
                    <span>{role}</span> <strong>{count}</strong>
                  </li>
                ))}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="panel">
      <h2>Синтаксический анализ</h2>

      <div className="text-input-section">
        <h3>Анализ текста</h3>
        <textarea
          placeholder="Введите текст для анализа..."
          value={directText}
          onChange={(e) => setDirectText(e.target.value)}
        />
        <button
          className="analyze-text-btn"
          onClick={handleDirectAnalyze}
          disabled={directAnalyzing || !directText.trim()}
        >
          {directAnalyzing ? 'Анализ...' : 'Анализировать текст'}
        </button>
      </div>

      {directAnalysis && (
        <>
          {renderStatistics(directAnalysis.statistics, directAnalysis.analysis_time_ms)}
          {directAnalysis.analysis.map((sentence) => renderSentenceTable(sentence))}
        </>
      )}

      <div className="upload-section" style={{ marginTop: '2rem' }}>
        <label className="upload-btn">
          {uploading ? 'Загрузка...' : 'Загрузить файл'}
          <input
            type="file"
            accept=".txt,.rtf"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>
        <span className="hint">(TXT, RTF)</span>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <div className="documents-list">
          <h3>Документы ({documents.length})</h3>
          {documents.length === 0 ? (
            <p>Документов пока нет. Загрузите файл.</p>
          ) : (
            <ul>
              {documents.map((doc) => (
                <li key={doc.id} className="document-item">
                  <div className="doc-info">
                    <strong>{doc.title}</strong>
                    <span className="word-count">{doc.metadata.word_count} слов</span>
                  </div>
                  <div className="doc-actions">
                    <button onClick={() => handleViewDocument(doc.id)}>Просмотр</button>
                    <button onClick={() => handleAnalyze(doc.id)} disabled={analyzing}>
                      Анализ
                    </button>
                    <button onClick={() => handleExportJson(doc.id, doc.title)}>
                      JSON
                    </button>
                    <button onClick={() => handleDelete(doc.id)} className="delete-btn">
                      Удалить
                    </button>
                  </div>
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
            <p><strong>Слов:</strong> {selectedDoc.metadata.word_count}</p>
            <p><strong>Символов:</strong> {selectedDoc.metadata.char_count}</p>
          </div>
          
          {editingDoc ? (
            <div className="edit-mode">
              <textarea
                className="edit-textarea"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={15}
              />
              <div className="edit-actions">
                <button onClick={handleEditSave} disabled={savingDoc}>
                  {savingDoc ? 'Сохранение...' : 'Сохранить'}
                </button>
                <button onClick={handleEditCancel} disabled={savingDoc}>
                  Отмена
                </button>
              </div>
            </div>
              ) : (
                <>
                  <div className="content">
                    <pre>{selectedDoc.content}</pre>
                  </div>
                  <div className="document-view-actions">
                    <button onClick={handleEditStart}>Редактировать</button>
                    <button onClick={() => { setSelectedDoc(null); setEditingDoc(null); }}>Закрыть</button>
                  </div>
                </>
              )}
        </div>
      )}

      {analysis && (
        <div style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Результаты анализа</h3>
            <button 
              className="relations-toggle-btn"
              onClick={() => setShowRelations(!showRelations)}
            >
              {showRelations ? 'Скрыть связи' : 'Показать связи'}
            </button>
          </div>
          
          {showRelations && renderRelationsPanel()}
          
          {renderStatistics(analysis.statistics, analysis.analysis_time_ms)}
          {analysis.analysis.map((sentence) => renderSentenceTable(sentence, analysis.document_id))}
        </div>
      )}

      {(showTrees && (dependencyTrees.length > 0 || constituencyTrees.length > 0)) && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Древовидные структуры</h3>
          {loadingTrees ? (
            <div className="loading">Загрузка деревьев...</div>
          ) : (
            <TreeVisualization 
              dependencyTrees={dependencyTrees} 
              constituencyTrees={constituencyTrees} 
            />
          )}
        </div>
      )}

      {analysis && (
        <div style={{ marginTop: '1rem' }}>
          <button 
            className="tree-toggle-btn"
            onClick={() => setShowTrees(!showTrees)}
          >
            {showTrees ? 'Скрыть деревья' : 'Показать деревья'}
          </button>
        </div>
      )}
    </div>
  );
}

export default SyntaxPanel;
