import uuid
from app.models.text import Text
from app.models.translation import Translation
from app.services.storage_service import StorageService
from app.inference.engine import InferenceEngine
from app.nlp.parser import NLPService

class TranslationController:
    def __init__(self):
        self.texts = StorageService.load_json('texts.json', [])
        self.translations = StorageService.load_json('translations.json', [])
        self.inference_engine = InferenceEngine()

    def process_text(self, content, source_lang, context_dict):
        if source_lang == 'auto':
            parsed = NLPService.parse(content)
            source_lang = parsed['detected_language']

        text_id = str(uuid.uuid4())
        context = context_dict or {}
        text = Text(text_id, content, source_language=source_lang, context=context)
        self.texts.append(text.__dict__)
        StorageService.save_json('texts.json', self.texts)
        return text_id

    def generate_draft(self, text_id, target_lang='en', dialect=''):
        text_data = next((t for t in self.texts if t['text_id'] == text_id), None)
        if not text_data: 
            raise ValueError("Text not found")

        content = text_data['content']
        source_lang = text_data.get('source_language', 'unknown')
        context = text_data.get('context', {})

        if source_lang == target_lang:
            return text_id, f"[INFO] Язык текста ({source_lang}) совпадает с целевым ({target_lang}). Перевод не требуется."

        enriched_context = self._enrich_context(context, dialect, content, source_lang, target_lang)
        translation_type = context.get('translation_type', 'adaptive')
        translated_content = self.inference_engine.infer_translation(
            content, enriched_context, 
            source_lang=source_lang, 
            target_lang=target_lang,
            translation_type=translation_type
        )

        draft = translated_content
        return text_id, draft

    def _enrich_context(self, context, dialect, text='', source_lang='ru', target_lang='en'):
        from app.knowledge.ontology import OntologyService
        enriched = OntologyService.analyze_cultural_context(text, source_lang, target_lang, context)
        if dialect:
            enriched['dialect'] = dialect
        return enriched

    def approve_translation(self, trans_id, final_text):
        trans = next((t for t in self.translations if t['trans_id'] == trans_id), None)
        if not trans:
            raise ValueError("Translation not found")

        trans['final_version'] = final_text
        trans['status'] = 'approved'
        StorageService.save_json('translations.json', self.translations)
        self._learn_from_feedback(trans)

    def _learn_from_feedback(self, trans):
        from app.knowledge.knowledge_graph import KnowledgeGraphService
        kg_service = KnowledgeGraphService()

        original = trans['content']
        draft = trans['draft']
        final = trans['final_version']

        kg_service.update_from_feedback(original, draft, final)

    def get_translation(self, trans_id):
        return next((t for t in self.translations if t['trans_id'] == trans_id), None)
