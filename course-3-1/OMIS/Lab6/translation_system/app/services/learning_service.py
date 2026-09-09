from app.knowledge.knowledge_graph import KnowledgeGraphService

class LearningService:
    @staticmethod
    def learn_from_feedback(original, draft, final, context):
        original_words = original.split()
        final_words = final.split()

        for i, orig_word in enumerate(original_words):
            if i < len(final_words):
                final_word = final_words[i]
                if orig_word != final_word:
                    KnowledgeGraphService().update_weight(orig_word, final_word, context, delta=0.1)