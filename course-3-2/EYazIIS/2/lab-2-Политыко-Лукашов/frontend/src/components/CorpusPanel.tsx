import { useState, useEffect } from 'react';
import { api, Document } from '../api/client';

interface UploadMetadata {
  author: string;
  date: string;
  genre: string;
  text_type: string;
}

function CorpusPanel() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploading, setUploading] = useState(false);
  const [editingDoc, setEditingDoc] = useState<Document | null>(null);
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMetadata, setUploadMetadata] = useState<UploadMetadata>({
    author: '',
    date: '',
    genre: '',
    text_type: 'кулинарный текст'
  });

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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setShowUploadModal(true);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      console.log(uploadMetadata)
      await api.loadFile(selectedFile, uploadMetadata);
      await loadDocuments();
      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadMetadata({
        author: '',
        date: '',
        genre: '',
        text_type: 'кулинарный текст'
      });
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
      }
    } catch (err) {
      setError('Не удалось удалить документ');
    }
  };

  const handleViewDocument = async (docId: string) => {
    try {
      const doc = await api.getDocument(docId);
      setSelectedDoc(doc);
    } catch (err) {
      setError('Не удалось загрузить документ');
    }
  };

  const handleEditStart = async (docId: string) => {
    try {
      const doc = await api.getDocument(docId);
      setEditingDoc(doc);
      setEditContent(doc.content);
    } catch (err) {
      setError('Не удалось загрузить документ');
    }
  };

  const handleEditSave = async () => {
    if (!editingDoc) return;
    try {
      setSaving(true);
      const updated = await api.updateDocument(editingDoc.id, editContent);
      setEditingDoc(null);
      await loadDocuments();
      if (selectedDoc?.id === updated.id) {
        setSelectedDoc(updated);
      }
    } catch (err) {
      setError('Не удалось сохранить документ');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="panel">
      <h2>Управление корпусом</h2>
      
      <div className="upload-section">
        <label className="upload-btn">
          {uploading ? 'Загрузка...' : 'Загрузить файл'}
          <input
            type="file"
            accept=".txt,.rtf,.pdf,.doc,.docx"
            onChange={handleFileSelect}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>
        <span className="hint">(TXT, RTF, PDF, DOC, DOCX)</span>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <div className="documents-list">
          <h3>Документы корпуса ({documents.length})</h3>
          {documents.length === 0 ? (
            <p>Документов пока нет. Загрузите файл.</p>
          ) : (
            <ul>
              {documents.map((doc) => (
                <li key={doc.id} className="document-item">
                  <div className="doc-info">
                    <strong>{doc.title}</strong>
                    <span className="word-count">{doc.word_count} слов</span>
                  </div>
                  <div className="doc-actions">
                    <button onClick={() => handleViewDocument(doc.id)}>Просмотр</button>
                    <button onClick={() => handleEditStart(doc.id)}>Редактировать</button>
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
            <p><strong>Автор:</strong> {selectedDoc.metadata.author || '-'}</p>
            <p><strong>Жанр:</strong> {selectedDoc.metadata.genre || '-'}</p>
            <p><strong>Дата:</strong> {selectedDoc.metadata.date || '-'}</p>
            <p><strong>Слов:</strong> {selectedDoc.metadata.word_count}</p>
            <p><strong>Символов:</strong> {selectedDoc.metadata.char_count}</p>
            <p><strong>Создан:</strong> {selectedDoc.metadata.created_at}</p>
          </div>
          <div className="content">
            <pre>{selectedDoc.content}</pre>
          </div>
          <button onClick={() => setSelectedDoc(null)}>Закрыть</button>
        </div>
      )}

      {editingDoc && (
        <div className="document-edit">
          <h3>Редактирование: {editingDoc.title}</h3>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            rows={20}
            className="edit-textarea"
          />
          <div className="edit-actions">
            <button onClick={handleEditSave} disabled={saving}>
              {saving ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button onClick={() => setEditingDoc(null)} disabled={saving}>
              Отмена
            </button>
          </div>
        </div>
      )}

      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Загрузка документа</h3>
            <div className="modal-content">
              <p><strong>Файл:</strong> {selectedFile?.name}</p>
              
              <div className="form-group">
                <label>Автор:</label>
                <input
                  type="text"
                  value={uploadMetadata.author}
                  onChange={e => setUploadMetadata({...uploadMetadata, author: e.target.value})}
                  placeholder="Автор текста"
                />
              </div>
              
              <div className="form-group">
                <label>Дата:</label>
                <input
                  type="text"
                  value={uploadMetadata.date}
                  onChange={e => setUploadMetadata({...uploadMetadata, date: e.target.value})}
                  placeholder="Год или дата"
                />
              </div>
              
              <div className="form-group">
                <label>Жанр:</label>
                <input
                  type="text"
                  value={uploadMetadata.genre}
                  onChange={e => setUploadMetadata({...uploadMetadata, genre: e.target.value})}
                  placeholder="Жанр текста"
                />
              </div>
              
              <div className="form-group">
                <label>Тип текста:</label>
                <input
                  type="text"
                  value={uploadMetadata.text_type}
                  onChange={e => setUploadMetadata({...uploadMetadata, text_type: e.target.value})}
                  placeholder="Тип текста"
                />
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={handleFileUpload} disabled={uploading}>
                {uploading ? 'Загрузка...' : 'Загрузить'}
              </button>
              <button onClick={() => setShowUploadModal(false)} disabled={uploading}>
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CorpusPanel;
