from app.services.storage_service import StorageService

class FeedbackLearningService:
    @staticmethod
    def save_feedback(original, draft, final, context=None):
        feedback = {
            "original": original,
            "draft": draft,
            "final": final,
            "context": context or {},
            "improvement": "manual correction"
        }
        data = StorageService.load_json("feedback.json", [])
        data.append(feedback)
        StorageService.save_json("feedback.json", data)

    @staticmethod
    def get_feedback_stats():
        data = StorageService.load_json("feedback.json", [])
        return len(data)