from app.nlp.parser import NLPService
from app.nlp.semantic_vectors import SemanticVectorService
from app.knowledge.ontology import OntologyService
from app.knowledge.knowledge_graph import KnowledgeGraphService

class InferenceEngine:
    def __init__(self):
        self.kg_service = KnowledgeGraphService()

    def infer_translation(self, text, context, source_lang='ru', target_lang='en', translation_type='adaptive'):
        adapted_context = context.copy()
        if translation_type == 'literal':
            adapted_context['style'] = 'neutral'
            adapted_context['translation_type'] = 'literal'
        elif translation_type == 'creative':
            if adapted_context.get('style') == 'neutral':
                adapted_context['style'] = 'poetic'
            adapted_context['translation_type'] = 'creative'
        else: 
            adapted_context['translation_type'] = 'adaptive'
<<<<<<< HEAD
        
        full_phrase_translation = self.kg_service.get_best_translation(text.lower(), adapted_context, source_lang, target_lang)
        if full_phrase_translation is not None and full_phrase_translation != text.lower() and full_phrase_translation != "":
            return full_phrase_translation.capitalize()
=======
        full_phrase_translation = self.kg_service.get_best_translation(text.lower(), adapted_context, source_lang, target_lang)
        
        if full_phrase_translation is not None and full_phrase_translation != text.lower() and full_phrase_translation != "":
            return full_phrase_translation.capitalize()

>>>>>>> d498ef2 (Update translation system: auth, localization, datasets, UI)
        parsed = NLPService.parse(text)
        translated_words = []

        for word in parsed["words"]:
            refined_context = OntologyService.infer_context(context)
<<<<<<< HEAD
            best_translation = self.kg_service.get_best_translation(word, refined_context, source_lang, target_lang)            
=======
            best_translation = self.kg_service.get_best_translation(word, refined_context, source_lang, target_lang)
        
>>>>>>> d498ef2 (Update translation system: auth, localization, datasets, UI)
            if best_translation == word and source_lang != 'en' and target_lang != 'en' and source_lang != target_lang:
                en_word = self.kg_service.get_best_translation(word, refined_context, source_lang, 'en')
                if en_word != word and en_word:
                    target_word = self.kg_service.get_best_translation(en_word, refined_context, 'en', target_lang)
                    if target_word != en_word and target_word:
                        best_translation = target_word
            translated_words.append(best_translation)
        result = " ".join(translated_words)
        
        if result.lower() == text.lower() and source_lang != 'en' and target_lang != 'en' and source_lang != target_lang:
            en_translation = self.kg_service.get_best_translation(text.lower(), adapted_context, source_lang, 'en')
            if en_translation != text.lower() and en_translation:
                final_translation = self.kg_service.get_best_translation(en_translation.lower(), adapted_context, 'en', target_lang)
                if final_translation != en_translation.lower() and final_translation:
                    result = final_translation
        return result.capitalize()

    def _find_similar_phrase(self, text, context):
        for phrase in self.kg_service.graph:
            if SemanticVectorService.cosine_similarity(
                SemanticVectorService.get_vector(text),
                SemanticVectorService.get_vector(phrase)
            ) > 0.7:
                translation = self.kg_service.get_best_translation(phrase, context)
                if translation != phrase:
                    return translation
        return None
