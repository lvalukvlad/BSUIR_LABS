from app.services.storage_service import StorageService
from app.services.feedback_learning_service import FeedbackLearningService
from app.services.report_service import ReportService

class AdminController:
    def get_statistics(self):
        return ReportService.get_detailed_statistics()