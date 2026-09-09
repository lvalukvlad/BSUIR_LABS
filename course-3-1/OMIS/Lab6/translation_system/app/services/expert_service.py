from app.models.user import Expert
from app.services.storage_service import StorageService

class ExpertService:
    def __init__(self):
        self.experts = StorageService.load_json('experts.json', [])
        self.consultations = StorageService.load_json('consultations.json', [])
    
    def create_expert(self, username, email, specialization=None):
        import uuid
        expert = {
            'expert_id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'specialization': specialization,
            'consultations_count': 0
        }
        self.experts.append(expert)
        StorageService.save_json('experts.json', self.experts)
        return expert
    
    def get_expert(self, expert_id):
        return next((e for e in self.experts if e['expert_id'] == expert_id), None)
    
    def create_consultation(self, translation_id, expert_id, advice, rating=None):
        import uuid
        from datetime import datetime
        consultation = {
            'consultation_id': str(uuid.uuid4()),
            'translation_id': translation_id,
            'expert_id': expert_id,
            'advice': advice,
            'rating': rating,
            'created_at': datetime.now().isoformat()
        }
        self.consultations.append(consultation)
        expert = self.get_expert(expert_id)
        if expert:
            expert['consultations_count'] = expert.get('consultations_count', 0) + 1
            StorageService.save_json('experts.json', self.experts)
        
        StorageService.save_json('consultations.json', self.consultations)
        return consultation
    
    def get_consultations_for_translation(self, translation_id):
        return [c for c in self.consultations if c['translation_id'] == translation_id]
    
    def get_experts_by_specialization(self, specialization):
        return [e for e in self.experts if e.get('specialization') == specialization]

