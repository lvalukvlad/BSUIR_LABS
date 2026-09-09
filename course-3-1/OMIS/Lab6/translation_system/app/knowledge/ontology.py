from app.services.cultural_analysis_service import CulturalAnalysisService

class OntologyService:
    CONTEXT_RULES = {
        "diplomatic": {"style": "formal", "audience": "official"},
        "medical": {"style": "formal", "domain": "healthcare"},
        "casual": {"style": "informal", "audience": "friends"},
        "poetic": {"style": "poetic", "domain": "literature"},
        "legal": {"style": "formal", "domain": "law"},
    }

    @staticmethod
    def infer_context(context):
        inferred = context.copy()
        for domain, rules in OntologyService.CONTEXT_RULES.items():
            if context.get("domain") == domain:
                for key, value in rules.items():
                    if key not in inferred:
                        inferred[key] = value
        return inferred
    
    @staticmethod
    def analyze_cultural_context(text, source_lang, target_lang, context):
        """
        Анализирует культурные особенности и добавляет их в контекст
        """
        cultural_notes = CulturalAnalysisService.analyze_cultural_features(
            text, source_lang, target_lang, context
        )
        inferred = OntologyService.infer_context(context)
        inferred['cultural_notes'] = cultural_notes
        return inferred