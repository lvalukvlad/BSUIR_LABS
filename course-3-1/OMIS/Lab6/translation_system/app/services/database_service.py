from app.models.database_models import (
    TranslationEntity, ChangeEntity, QualityEntity, AdminEntity,
    DictionaryEntity, CorpusEntity, ModelEntity
)
from app.services.storage_service import StorageService

class DatabaseService:
    def __init__(self):
        self.translations = StorageService.load_json('translations_entities.json', [])
        self.changes = StorageService.load_json('changes_entities.json', [])
        self.qualities = StorageService.load_json('qualities_entities.json', [])
        self.admins = StorageService.load_json('admins_entities.json', [])
        self.dictionaries = StorageService.load_json('dictionaries_entities.json', [])
        self.corpora = StorageService.load_json('corpora_entities.json', [])
        self.models = StorageService.load_json('models_entities.json', [])
    
    def create_translation(self, text_id, content, draft, source_lang, target_lang):
        trans = TranslationEntity(text_id, content, draft, source_lang, target_lang)
        self.translations.append(trans.to_dict())
        StorageService.save_json('translations_entities.json', self.translations)
        return trans
    
    def get_translation(self, trans_id):
        return next((t for t in self.translations if t['trans_id'] == trans_id), None)
    
    def create_change(self, trans_id, old_text, new_text, change_type='edit', user_id=None):
        change = ChangeEntity(trans_id, old_text, new_text, change_type, user_id)
        self.changes.append(change.to_dict())
        trans = self.get_translation(trans_id)
        if trans:
            if 'change_ids' not in trans:
                trans['change_ids'] = []
            trans['change_ids'].append(change.change_id)
            StorageService.save_json('translations_entities.json', self.translations)
        
        StorageService.save_json('changes_entities.json', self.changes)
        return change
    
    def create_quality(self, trans_id, score, metrics=None, reviewer_id=None):
        quality = QualityEntity(trans_id, score, metrics, reviewer_id)
        self.qualities.append(quality.to_dict())
        trans = self.get_translation(trans_id)
        if trans:
            trans['quality_id'] = quality.quality_id
            StorageService.save_json('translations_entities.json', self.translations)
        
        StorageService.save_json('qualities_entities.json', self.qualities)
        return quality
    
    def create_admin(self, username, email, role='admin'):
        admin = AdminEntity(username, email, role)
        self.admins.append(admin.to_dict())
        StorageService.save_json('admins_entities.json', self.admins)
        return admin
    
    def create_dictionary(self, name, source_lang, target_lang, entries=None):
        dictionary = DictionaryEntity(name, source_lang, target_lang, entries)
        self.dictionaries.append(dictionary.to_dict())
        StorageService.save_json('dictionaries_entities.json', self.dictionaries)
        return dictionary
    
    def create_corpus(self, name, source_lang, target_lang, texts=None):
        corpus = CorpusEntity(name, source_lang, target_lang, texts)
        self.corpora.append(corpus.to_dict())
        StorageService.save_json('corpora_entities.json', self.corpora)
        return corpus
    
    def create_model(self, name, model_type, source_lang, target_lang, version='1.0'):
        model = ModelEntity(name, model_type, source_lang, target_lang, version)
        self.models.append(model.to_dict())
        StorageService.save_json('models_entities.json', self.models)
        return model

