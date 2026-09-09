import uuid
from datetime import datetime

class TranslationEntity:
    """Сущность перевода с отдельным ID"""
    def __init__(self, text_id, content, draft, source_lang, target_lang, status='draft'):
        self.trans_id = str(uuid.uuid4())
        self.text_id = text_id
        self.content = content
        self.draft = draft
        self.final_version = None
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.quality_id = None  # Ссылка на ID качества
        self.change_ids = []  # Список ID изменений
        
    def to_dict(self):
        return {
            'trans_id': self.trans_id,
            'text_id': self.text_id,
            'content': self.content,
            'draft': self.draft,
            'final_version': self.final_version,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'status': self.status,
            'created_at': self.created_at,
            'quality_id': self.quality_id,
            'change_ids': self.change_ids
        }

class ChangeEntity:
    """Сущность изменения перевода с отдельным ID"""
    def __init__(self, trans_id, old_text, new_text, change_type='edit', user_id=None):
        self.change_id = str(uuid.uuid4())
        self.trans_id = trans_id
        self.old_text = old_text
        self.new_text = new_text
        self.change_type = change_type  # 'edit', 'approve', 'reject'
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'change_id': self.change_id,
            'trans_id': self.trans_id,
            'old_text': self.old_text,
            'new_text': self.new_text,
            'change_type': self.change_type,
            'user_id': self.user_id,
            'created_at': self.created_at
        }

class QualityEntity:
    """Сущность оценки качества перевода с отдельным ID"""
    def __init__(self, trans_id, score, metrics=None, reviewer_id=None):
        self.quality_id = str(uuid.uuid4())
        self.trans_id = trans_id
        self.score = score  
        self.metrics = metrics or {}  
        self.reviewer_id = reviewer_id
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'quality_id': self.quality_id,
            'trans_id': self.trans_id,
            'score': self.score,
            'metrics': self.metrics,
            'reviewer_id': self.reviewer_id,
            'created_at': self.created_at
        }

class AdminEntity:
    """Сущность администратора с отдельным ID"""
    def __init__(self, username, email, role='admin'):
        self.admin_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.role = role
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }

class DictionaryEntity:
    """Сущность словаря с отдельным ID"""
    def __init__(self, name, source_lang, target_lang, entries=None):
        self.dict_id = str(uuid.uuid4())
        self.name = name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.entries = entries or []
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'dict_id': self.dict_id,
            'name': self.name,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'entries': self.entries,
            'created_at': self.created_at
        }

class CorpusEntity:
    """Сущность корпуса текстов с отдельным ID"""
    def __init__(self, name, source_lang, target_lang, texts=None):
        self.corpus_id = str(uuid.uuid4())
        self.name = name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.texts = texts or []
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'corpus_id': self.corpus_id,
            'name': self.name,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'texts': self.texts,
            'created_at': self.created_at
        }

class ModelEntity:
    """Сущность модели машинного обучения с отдельным ID"""
    def __init__(self, name, model_type, source_lang, target_lang, version='1.0'):
        self.model_id = str(uuid.uuid4())
        self.name = name
        self.model_type = model_type  
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.version = version
        self.created_at = datetime.now().isoformat()
        self.performance_metrics = {}
        
    def to_dict(self):
        return {
            'model_id': self.model_id,
            'name': self.name,
            'model_type': self.model_type,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'version': self.version,
            'created_at': self.created_at,
            'performance_metrics': self.performance_metrics
        }

