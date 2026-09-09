from app.services.storage_service import StorageService
from app.services.feedback_learning_service import FeedbackLearningService
from app.knowledge.knowledge_graph import KnowledgeGraphService


class ReportService:
    @staticmethod
    def get_detailed_statistics():
        translations = StorageService.load_json('translations.json', [])
        feedbacks = StorageService.load_json('feedback.json', [])
        total = len(translations)
        approved = len([t for t in translations if t.get('final_version')])
        avg_quality = sum(t.get('quality_score', 0) for t in translations) / total if total > 0 else 0
        total_feedback = len(feedbacks)

        kg_service = KnowledgeGraphService()
        learned_rules_count = sum(len(translations) for translations in kg_service.graph.values())

        frequent_changes = {}
        for fb in feedbacks:
            draft_words = fb['draft'].split()
            final_words = fb['final'].split()
            for dw, fw in zip(draft_words, final_words):
                if dw != fw:
                    key = (dw, fw)
                    frequent_changes[key] = frequent_changes.get(key, 0) + 1
        sorted_changes = sorted(frequent_changes.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_translations': total,
            'approved': approved,
            'avg_quality': round(avg_quality, 2),
            'total_feedback': total_feedback,
            'learned_rules_count': learned_rules_count,
            'top_changes': [
                {"from": k[0], "to": k[1], "count": v} for k, v in sorted_changes
            ]
        }