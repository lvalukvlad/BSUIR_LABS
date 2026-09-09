from app.inference.engine import InferenceEngine
from app.knowledge.ontology import OntologyService
import re

class LocalizationController:
    @staticmethod
    def generate_variants(draft_text, original_context):
        match = re.search(r'\[DRAFT \| (.+?)\] (.+)', draft_text)
        if not match:
            original_text = draft_text
        else:
            original_text = match.group(2)

        formal_context = original_context.copy()
        formal_context["style"] = "formal"
        formal_context = OntologyService.infer_context(formal_context)
        formal_translation = InferenceEngine().infer_translation(original_text, formal_context)

        casual_context = original_context.copy()
        casual_context["style"] = "casual"
        casual_context = OntologyService.infer_context(casual_context)
        casual_translation = InferenceEngine().infer_translation(original_text, casual_context)

        poetic_context = original_context.copy()
        poetic_context["style"] = "poetic"
        poetic_context = OntologyService.infer_context(poetic_context)
        poetic_translation = InferenceEngine().infer_translation(original_text, poetic_context)

        return [
            f"[FORMAL] {formal_translation}",
            f"[CASUAL] {casual_translation}",
            f"[POETIC] {poetic_translation}"
        ]